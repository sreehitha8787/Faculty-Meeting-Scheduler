from django.db import models
from django.contrib.auth.models import User

class FacultyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    staff_id = models.CharField(max_length=10, unique=True, null=True, blank=True)
    staff_id = models.CharField(max_length=10, unique=True, null=True, blank=True)
    profile_picture = models.URLField(blank=True)
    department = models.CharField(max_length=100)
    faculty_position = models.CharField(max_length=120, default='Faculty member')
    is_department_head = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class TimeTable(models.Model):
    faculty = models.ForeignKey(FacultyProfile, on_delete=models.CASCADE)
    day = models.CharField(max_length=10)
    start_time = models.TimeField()
    end_time = models.TimeField()
    class_room = models.CharField(max_length=100)
      # New field

    class Meta:
        unique_together = ('faculty', 'day', 'start_time')

class MeetingSlot(models.Model):
    faculty = models.ForeignKey(FacultyProfile, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ('faculty', 'date', 'start_time')


class ScheduledMeeting(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('cancelled', 'Cancelled'),
    )
    organizer = models.ForeignKey(FacultyProfile, on_delete=models.CASCADE, related_name='organized_meetings')
    title = models.CharField(max_length=160)
    agenda = models.TextField(blank=True)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')
    participants = models.ManyToManyField(FacultyProfile, through='MeetingParticipant', related_name='invited_meetings')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'start_time']


class MeetingParticipant(models.Model):
    meeting = models.ForeignKey(ScheduledMeeting, on_delete=models.CASCADE)
    faculty = models.ForeignKey(FacultyProfile, on_delete=models.CASCADE)
    response = models.CharField(max_length=10, choices=(('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined')), default='pending')

    class Meta:
        unique_together = ('meeting', 'faculty')


class Notification(models.Model):
    recipient = models.ForeignKey(FacultyProfile, on_delete=models.CASCADE, related_name='notifications')
    meeting = models.ForeignKey(ScheduledMeeting, on_delete=models.CASCADE, null=True, blank=True)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class PushSubscription(models.Model):
    faculty = models.ForeignKey(FacultyProfile, on_delete=models.CASCADE, related_name='push_subscriptions')
    endpoint = models.URLField(max_length=500, unique=True)
    p256dh = models.TextField()
    auth = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']


class PublicHoliday(models.Model):
    """University-approved holiday; only active records block meeting bookings."""
    date = models.DateField(unique=True)
    name = models.CharField(max_length=160)
    region = models.CharField(max_length=80, default='All India')
    source = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f'{self.date}: {self.name}'


class AcademicEvent(models.Model):
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    department = models.CharField(max_length=100, blank=True)
    published_by = models.ForeignKey(FacultyProfile, on_delete=models.PROTECT, related_name='published_academic_events')
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'start_time', 'title']
