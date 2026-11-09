from datetime import datetime, time, timedelta
import json

from django.contrib.auth import authenticate, get_user_model
from django.db import models
from django.core.mail import send_mail
from django.conf import settings
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils.dateparse import parse_date, parse_time
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import FacultyProfile, TimeTable, MeetingSlot, PublicHoliday, ScheduledMeeting, MeetingParticipant, Notification, AcademicEvent, PushSubscription
from .crypto import encrypt, decrypt
from .serializers import FacultyProfileSerializer, TimeTableSerializer, MeetingSlotSerializer

User = get_user_model()


def _send_browser_push(faculty, message):
    if not settings.VAPID_PRIVATE_KEY or not settings.VAPID_PUBLIC_KEY:
        return
    from pywebpush import WebPushException, webpush
    payload = {
        'title': 'MU Staff Calendar',
        'body': message,
        'url': '/home/calendar',
    }
    for subscription in faculty.push_subscriptions.all():
        try:
            webpush(
                subscription_info={
                    'endpoint': subscription.endpoint,
                    'keys': {'p256dh': decrypt(subscription.p256dh), 'auth': decrypt(subscription.auth)},
                },
                data=json.dumps(payload),
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={'sub': f'mailto:{settings.VAPID_ADMIN_EMAIL}'},
            )
        except WebPushException as error:
            if getattr(error, 'response', None) is not None and error.response.status_code in (404, 410):
                subscription.delete()


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Authenticate by username or email and return a short-lived access token."""
    username = (request.data.get('username') or '').strip().lower()
    password = request.data.get('password') or ''

    if not username or not password:
        return Response(
            {'error': 'Staff username and password are required.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Staff usernames are alphanumeric only; email login is intentionally disabled.
    if not username.isalnum():
        return Response({'error': 'Use your alphanumeric staff username.'}, status=status.HTTP_400_BAD_REQUEST)
    user = authenticate(request=request, username=username, password=password)

    if user is None:
        try:
            matching_user = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            matching_user = None

        if matching_user is not None:
            user = authenticate(
                request=request,
                username=matching_user.username,
                password=password
            )

    if user is None:
        return Response({'error': 'Invalid staff username or password.'}, status=status.HTTP_401_UNAUTHORIZED)

    if not user.is_active:
        return Response({'error': 'This account is disabled.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        profile = FacultyProfile.objects.select_related('user').get(user=user)
    except FacultyProfile.DoesNotExist:
        return Response({'error': 'Faculty profile not found. Please contact the administrator.'}, status=status.HTTP_404_NOT_FOUND)

    refresh = RefreshToken.for_user(user)
    return Response({
        'message': 'Login successful',
        'profile': FacultyProfileSerializer(profile).data,
        'token': str(refresh.access_token),
        'refresh': str(refresh),
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    # The client discards its access/refresh tokens. Token blacklisting is not enabled in this project.
    return Response({'message': 'Logged out successfully. Please discard your local tokens.'}, status=status.HTTP_200_OK)


class TimeTableViewSet(viewsets.ModelViewSet):
    serializer_class = TimeTableSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TimeTable.objects.filter(faculty__user=self.request.user).select_related('faculty', 'faculty__user')

    def perform_create(self, serializer):
        profile = FacultyProfile.objects.get(user=self.request.user)
        serializer.save(faculty=profile)


class MeetingSlotViewSet(viewsets.ModelViewSet):
    serializer_class = MeetingSlotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MeetingSlot.objects.filter(faculty__user=self.request.user).select_related('faculty', 'faculty__user')

    def perform_create(self, serializer):
        profile = FacultyProfile.objects.get(user=self.request.user)
        serializer.save(faculty=profile)


def _parse_date_time(value, parser, field_name):
    parsed = parser(value) if value else None
    if parsed is None:
        raise ValueError(f'{field_name} must be provided in a valid format.')
    return parsed


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_availability(request):
    """Check availability at a specific date and time (or a single time point)."""
    try:
        selected_date = _parse_date_time(request.query_params.get('date'), parse_date, 'date')
        selected_time = _parse_date_time(request.query_params.get('time'), parse_time, 'time')
    except ValueError as exc:
        return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    day_name = selected_date.strftime('%A')
    results = []
    for profile in FacultyProfile.objects.select_related('user').all():
        has_class = TimeTable.objects.filter(
            faculty=profile,
            day__iexact=day_name,
            start_time__lte=selected_time,
            end_time__gt=selected_time,
        ).exists()
        has_meeting = MeetingSlot.objects.filter(
            faculty=profile,
            date=selected_date,
            start_time__lte=selected_time,
            end_time__gt=selected_time,
            is_available=False,
        ).exists()
        has_scheduled_meeting = ScheduledMeeting.objects.filter(
            models.Q(organizer=profile) | models.Q(participants=profile),
            date=selected_date,
            start_time__lte=selected_time,
            end_time__gt=selected_time,
            status__in=('pending', 'accepted'),
        ).exists()
        results.append({'username': profile.user.username, 'department': profile.department,
                        'available': not (has_class or has_meeting or has_scheduled_meeting)})
    return Response(results)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_all_entries(request):
    """Administrative diagnostic endpoint; never expose all staff data to ordinary users."""
    faculty_profiles = FacultyProfile.objects.select_related('user').all()
    timetables = TimeTable.objects.all()
    meeting_slots = MeetingSlot.objects.select_related('faculty', 'faculty__user').all()
    return Response({
        'faculty_profiles': FacultyProfileSerializer(faculty_profiles, many=True).data,
        'timetables': TimeTableSerializer(timetables, many=True).data,
        'meetings': MeetingSlotSerializer(meeting_slots, many=True).data,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_timetable(request):
    """Return only the authenticated staff member's timetable; username query params are ignored."""
    try:
        profile = FacultyProfile.objects.get(user=request.user)
    except FacultyProfile.DoesNotExist:
        return Response({'error': 'Faculty profile not found.'}, status=status.HTTP_404_NOT_FOUND)
    entries = TimeTable.objects.filter(faculty=profile).order_by('day', 'start_time')
    return Response(TimeTableSerializer(entries, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_timetables(request):
    try:
        profile = FacultyProfile.objects.get(user=request.user)
    except FacultyProfile.DoesNotExist:
        return Response({'error': 'Faculty profile not found.'}, status=status.HTTP_404_NOT_FOUND)
    entries = TimeTable.objects.filter(faculty=profile).order_by('day', 'start_time')
    return Response(TimeTableSerializer(entries, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_users_with_timetables(request):
    try:
        profile = FacultyProfile.objects.select_related('user').get(user=request.user)
    except FacultyProfile.DoesNotExist:
        return Response({'error': 'Faculty profile not found.'}, status=status.HTTP_404_NOT_FOUND)
    timetables = TimeTable.objects.filter(faculty=profile).order_by('day', 'start_time')
    return Response({
        'username': profile.user.username,
        'email': profile.user.email,
        'department': profile.department,
        'timetables': TimeTableSerializer(timetables, many=True).data,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_faculty_availability(request):
    """Return staff availability for a specific date and time interval."""
    date_value = request.query_params.get('date')
    start_value = request.query_params.get('start_time')
    end_value = request.query_params.get('end_time')
    if not date_value or not start_value or not end_value:
        return Response({'error': 'Date, start_time, and end_time are required.'}, status=status.HTTP_400_BAD_REQUEST)

    selected_date = parse_date(date_value)
    start_time = parse_time(start_value)
    end_time = parse_time(end_value)
    if selected_date is None:
        return Response({'error': 'Date must use YYYY-MM-DD format.'}, status=status.HTTP_400_BAD_REQUEST)
    if start_time is None or end_time is None:
        return Response({'error': 'Times must use HH:MM or HH:MM:SS format.'}, status=status.HTTP_400_BAD_REQUEST)
    if start_time >= end_time:
        return Response({'error': 'End time must be later than start time.'}, status=status.HTTP_400_BAD_REQUEST)

    from .models import PublicHoliday
    holiday = PublicHoliday.objects.filter(date=selected_date, is_active=True).first()
    if holiday:
        return Response({'error': f'{holiday.name} is a public holiday. Meeting scheduling is blocked.', 'holiday': {'date': holiday.date.isoformat(), 'name': holiday.name}}, status=status.HTTP_409_CONFLICT)

    day_name = selected_date.strftime('%A')
    available_faculty = []
    busy_faculty = []
    profiles = FacultyProfile.objects.select_related('user').all()

    for profile in profiles:
        has_class = TimeTable.objects.filter(
            faculty=profile,
            day__iexact=day_name,
            start_time__lt=end_time,
            end_time__gt=start_time,
        ).exists()
        has_meeting = MeetingSlot.objects.filter(
            faculty=profile,
            date=selected_date,
            start_time__lt=end_time,
            end_time__gt=start_time,
            is_available=False,
        ).exists()
        has_scheduled_meeting = ScheduledMeeting.objects.filter(
            models.Q(organizer=profile) | models.Q(participants=profile),
            date=selected_date,
            start_time__lt=end_time,
            end_time__gt=start_time,
            status__in=('pending', 'accepted'),
        ).exists()
        item = {'username': profile.user.username, 'department': profile.department}
        (busy_faculty if has_class or has_meeting or has_scheduled_meeting else available_faculty).append(item)

    return Response({'available_faculty': available_faculty, 'busy_faculty': busy_faculty})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_faculty(request):
    """Search faculty by username, name, or staff ID for meeting invitations."""
    query = (request.query_params.get('q') or '').strip()
    if len(query) < 1:
        return Response([])
    profiles = FacultyProfile.objects.select_related('user').filter(
        models.Q(user__username__icontains=query) |
        models.Q(user__first_name__icontains=query) |
        models.Q(user__last_name__icontains=query) |
        models.Q(staff_id__icontains=query)
    )[:10]
    return Response([{
        'username': profile.user.username,
        'name': profile.user.get_full_name() or profile.user.username,
        'staff_id': profile.staff_id,
        'department': profile.department,
    } for profile in profiles])


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def faculty_date_slots(request):
    """Return one-hour slots free for all selected faculty on a date."""
    usernames = [value.strip() for value in (request.query_params.get('usernames') or '').split(',') if value.strip()]
    selected_date = parse_date(request.query_params.get('date') or '')
    if not usernames or not selected_date:
        return Response({'error': 'Select faculty and a valid date.'}, status=status.HTTP_400_BAD_REQUEST)
    if PublicHoliday.objects.filter(date=selected_date, is_active=True).exists():
        return Response({'slots': [], 'message': 'Meeting scheduling is blocked on this public holiday.'})

    profiles = list(FacultyProfile.objects.select_related('user').filter(user__username__in=usernames))
    if len(profiles) != len(set(usernames)):
        return Response({'error': 'One or more selected faculty members could not be found.'}, status=status.HTTP_400_BAD_REQUEST)

    slots = []
    slot_start = time(8, 0)
    while slot_start < time(17, 0):
        slot_end = (datetime.combine(selected_date, slot_start) + timedelta(hours=1)).time()
        available = True
        for profile in profiles:
            has_class = TimeTable.objects.filter(
                faculty=profile, day__iexact=selected_date.strftime('%A'),
                start_time__lt=slot_end, end_time__gt=slot_start,
            ).exists()
            has_meeting = MeetingSlot.objects.filter(
                faculty=profile, date=selected_date, is_available=False,
                start_time__lt=slot_end, end_time__gt=slot_start,
            ).exists()
            has_scheduled_meeting = ScheduledMeeting.objects.filter(
                models.Q(organizer=profile) | models.Q(participants=profile),
                date=selected_date, start_time__lt=slot_end, end_time__gt=slot_start,
                status__in=('pending', 'accepted'),
            ).exists()
            if has_class or has_meeting or has_scheduled_meeting:
                available = False
                break
        if available:
            slots.append({'start_time': slot_start.strftime('%H:%M'), 'end_time': slot_end.strftime('%H:%M')})
        slot_start = slot_end
    return Response({'date': selected_date.isoformat(), 'slots': slots})


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def scheduled_meetings(request):
    try:
        organizer = FacultyProfile.objects.get(user=request.user)
    except FacultyProfile.DoesNotExist:
        return Response({'error': 'Faculty profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        meetings = ScheduledMeeting.objects.filter(
            models.Q(organizer=organizer) | models.Q(participants=organizer)
        ).distinct().prefetch_related('participants__user')
        return Response([{
            'id': meeting.id,
            'title': meeting.title,
            'agenda': meeting.agenda,
            'date': meeting.date.isoformat(),
            'start_time': meeting.start_time.isoformat(),
            'end_time': meeting.end_time.isoformat(),
            'status': meeting.status,
            'organizer': meeting.organizer.user.username,
            'participants': [{
                'username': participant.user.username,
                'response': MeetingParticipant.objects.get(meeting=meeting, faculty=participant).response,
            } for participant in meeting.participants.all()],
        } for meeting in meetings])

    payload = request.data
    title = (payload.get('title') or '').strip()
    participant_usernames = payload.get('participant_usernames') or []
    selected_date = parse_date(payload.get('date') or '')
    start_time = parse_time(payload.get('start_time') or '')
    end_time = parse_time(payload.get('end_time') or '')
    if not title or not selected_date or not start_time or not end_time or start_time >= end_time:
        return Response({'error': 'Title, date, valid start time, and later end time are required.'}, status=status.HTTP_400_BAD_REQUEST)
    if not isinstance(participant_usernames, list) or not participant_usernames:
        return Response({'error': 'Select at least one faculty member to invite.'}, status=status.HTTP_400_BAD_REQUEST)
    holiday = PublicHoliday.objects.filter(date=selected_date, is_active=True).first()
    if holiday:
        return Response({'error': f'{holiday.name} is a public holiday. Meeting scheduling is blocked.'}, status=status.HTTP_409_CONFLICT)
    participants = list(FacultyProfile.objects.select_related('user').filter(user__username__in=participant_usernames).exclude(pk=organizer.pk))
    if len(participants) != len(set(participant_usernames)):
        return Response({'error': 'One or more selected faculty members could not be found.'}, status=status.HTTP_400_BAD_REQUEST)
    invitees = [organizer] + participants
    conflicts = [
        profile.user.username for profile in invitees
        if MeetingSlot.objects.filter(
            faculty=profile, date=selected_date, start_time__lt=end_time,
            end_time__gt=start_time, is_available=False,
        ).exists()
        or TimeTable.objects.filter(
            faculty=profile, day__iexact=selected_date.strftime('%A'),
            start_time__lt=end_time, end_time__gt=start_time,
        ).exists()
        or ScheduledMeeting.objects.filter(
            models.Q(organizer=profile) | models.Q(participants=profile),
            date=selected_date, start_time__lt=end_time, end_time__gt=start_time,
            status__in=('pending', 'accepted'),
        ).exists()
    ]
    if conflicts:
        return Response({'error': f'The selected time is busy for: {", ".join(conflicts)}.'}, status=status.HTTP_409_CONFLICT)
    meeting = ScheduledMeeting.objects.create(
        organizer=organizer, title=title, agenda=(payload.get('agenda') or '').strip(),
        date=selected_date, start_time=start_time, end_time=end_time,
    )
    MeetingParticipant.objects.bulk_create([MeetingParticipant(meeting=meeting, faculty=participant) for participant in participants])
    Notification.objects.bulk_create([
        Notification(recipient=participant, meeting=meeting, message=f'{organizer.user.get_full_name() or organizer.user.username} invited you to "{title}" on {selected_date.isoformat()}.')
        for participant in participants
    ])
    for participant in participants:
        notification = Notification.objects.filter(recipient=participant, meeting=meeting).latest('created_at')
        payload = {'id': notification.id, 'message': notification.message, 'meeting_id': meeting.id, 'can_respond': True}
        async_to_sync(get_channel_layer().group_send)(
            f'notifications_{participant.user_id}', {'type': 'notification_event', 'payload': payload}
        )
        if participant.user.email:
            send_mail(
                f'Meeting invitation: {title}',
                notification.message,
                None,
                [participant.user.email],
                fail_silently=False,
            )
        _send_browser_push(participant, notification.message)
    return Response({'id': meeting.id, 'message': 'Meeting scheduled and invitations sent.'}, status=status.HTTP_201_CREATED)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def meeting_response(request, meeting_id):
    profile = FacultyProfile.objects.get(user=request.user)
    response_value = request.data.get('response')
    if response_value not in ('accepted', 'declined'):
        return Response({'error': 'Response must be accepted or declined.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        participant = MeetingParticipant.objects.select_related('meeting', 'meeting__organizer__user').get(
            meeting_id=meeting_id, faculty=profile
        )
    except MeetingParticipant.DoesNotExist:
        return Response({'error': 'Meeting invitation not found.'}, status=status.HTTP_404_NOT_FOUND)
    participant.response = response_value
    participant.save(update_fields=['response'])
    meeting = participant.meeting
    if response_value == 'declined':
        meeting.status = 'declined'
    elif all(item.response == 'accepted' for item in meeting.meetingparticipant_set.all()):
        meeting.status = 'accepted'
    meeting.save(update_fields=['status'])
    Notification.objects.create(
        recipient=meeting.organizer,
        meeting=meeting,
        message=f'{profile.user.get_full_name() or profile.user.username} {response_value} the invitation for "{meeting.title}".',
    )
    async_to_sync(get_channel_layer().group_send)(
        f'notifications_{meeting.organizer.user_id}',
        {'type': 'notification_event', 'payload': {'meeting_id': meeting.id, 'message': f'{profile.user.get_full_name() or profile.user.username} {response_value} the invitation for "{meeting.title}".'}},
    )
    return Response({'message': f'Invitation {response_value}.', 'status': meeting.status})


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def notifications(request):
    profile = FacultyProfile.objects.get(user=request.user)
    if request.method == 'PATCH':
        Notification.objects.filter(recipient=profile, is_read=False).update(is_read=True)
        return Response({'message': 'Notifications marked as read.'})
    rows = Notification.objects.filter(recipient=profile)[:30]
    return Response([{
        'id': row.id, 'message': row.message, 'is_read': row.is_read,
        'created_at': row.created_at.isoformat(), 'meeting_id': row.meeting_id,
        'can_respond': bool(row.meeting_id and MeetingParticipant.objects.filter(meeting_id=row.meeting_id, faculty=profile).exists()),
    } for row in rows])


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def push_subscriptions(request):
    profile = FacultyProfile.objects.get(user=request.user)
    if request.method == 'DELETE':
        endpoint = request.data.get('endpoint') or request.query_params.get('endpoint')
        PushSubscription.objects.filter(faculty=profile, endpoint=endpoint).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    subscription = request.data
    endpoint = subscription.get('endpoint')
    keys = subscription.get('keys') or {}
    if not endpoint or not keys.get('p256dh') or not keys.get('auth'):
        return Response({'error': 'A complete browser push subscription is required.'}, status=status.HTTP_400_BAD_REQUEST)
    PushSubscription.objects.update_or_create(
        endpoint=endpoint,
        defaults={'faculty': profile, 'p256dh': encrypt(keys['p256dh']), 'auth': encrypt(keys['auth'])},
    )
    return Response({'message': 'Browser notifications enabled.'}, status=status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def academic_events(request):
    profile = FacultyProfile.objects.get(user=request.user)
    if request.method == 'GET':
        queryset = AcademicEvent.objects.filter(is_published=True).filter(
            models.Q(department='') | models.Q(department=profile.department)
        )
        return Response([{
            'id': event.id, 'title': event.title, 'description': event.description,
            'date': event.date.isoformat(), 'start_time': event.start_time.isoformat() if event.start_time else None,
            'end_time': event.end_time.isoformat() if event.end_time else None,
            'department': event.department,
        } for event in queryset])
    if not (profile.is_department_head or request.user.is_staff):
        return Response({'error': 'Only department heads or administrators can publish academic events.'}, status=status.HTTP_403_FORBIDDEN)
    payload = request.data
    title = (payload.get('title') or '').strip()
    selected_date = parse_date(payload.get('date') or '')
    department = (payload.get('department') or '').strip()
    if not title or not selected_date:
        return Response({'error': 'Title and date are required.'}, status=status.HTTP_400_BAD_REQUEST)
    if department and department != profile.department and not request.user.is_staff:
        return Response({'error': 'Department heads may publish only for their own department.'}, status=status.HTTP_403_FORBIDDEN)
    event = AcademicEvent.objects.create(
        title=title, description=(payload.get('description') or '').strip(),
        date=selected_date, department=department, published_by=profile, is_published=True,
    )
    return Response({'id': event.id, 'message': 'Academic event published.'}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def public_holidays(request):
    """List active approved holidays. Date ranges are optional ISO YYYY-MM-DD."""
    from .models import PublicHoliday
    queryset = PublicHoliday.objects.filter(is_active=True)
    start = request.query_params.get('start')
    end = request.query_params.get('end')
    if start:
        parsed = parse_date(start)
        if not parsed:
            return Response({'error': 'start must use YYYY-MM-DD.'}, status=400)
        queryset = queryset.filter(date__gte=parsed)
    if end:
        parsed = parse_date(end)
        if not parsed:
            return Response({'error': 'end must use YYYY-MM-DD.'}, status=400)
        queryset = queryset.filter(date__lte=parsed)
    return Response([{'id': h.id, 'date': h.date.isoformat(), 'name': h.name,
                      'region': h.region, 'source': h.source} for h in queryset])
