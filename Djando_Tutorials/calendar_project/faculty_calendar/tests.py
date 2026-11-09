from datetime import date, time

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import FacultyProfile, TimeTable, MeetingSlot, Notification, PushSubscription


class AuthenticationAndAvailabilityTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='sree', email='sree@example.com', password='StrongPass123!')
        self.profile = FacultyProfile.objects.create(user=self.user, department='CSE')
        self.other_user = User.objects.create_user(username='other', password='StrongPass123!')
        self.other_profile = FacultyProfile.objects.create(user=self.other_user, department='ECE')

    def test_login_returns_access_token_and_profile(self):
        response = self.client.post(
            reverse('login'),
            {'username': 'sree', 'password': 'StrongPass123!'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['profile']['user']['username'], 'sree')

    def test_private_timetable_endpoint_requires_authentication(self):
        response = self.client.get(reverse('get_timetable'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_timetable_endpoint_only_returns_authenticated_users_entries(self):
        own = TimeTable.objects.create(
            faculty=self.profile, day='Wednesday', start_time=time(9, 0),
            end_time=time(10, 0), class_room='Room 1',
        )
        TimeTable.objects.create(
            faculty=self.other_profile, day='Wednesday', start_time=time(10, 0),
            end_time=time(11, 0), class_room='Room 2',
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('get_timetable') + '?username=other')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([row['id'] for row in response.data], [own.id])

    def test_availability_uses_real_date_and_overlap_logic(self):
        selected_date = date(2026, 10, 28)  # Wednesday
        TimeTable.objects.create(
            faculty=self.profile, day='Wednesday', start_time=time(9, 0),
            end_time=time(10, 0), class_room='Room 1',
        )
        MeetingSlot.objects.create(
            faculty=self.other_profile, date=selected_date,
            start_time=time(11, 0), end_time=time(12, 0), is_available=False,
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('get_faculty_availability'), {
            'date': selected_date.isoformat(), 'start_time': '09:30', 'end_time': '10:30',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        busy_usernames = {row['username'] for row in response.data['busy_faculty']}
        available_usernames = {row['username'] for row in response.data['available_faculty']}
        self.assertIn('sree', busy_usernames)
        self.assertIn('other', available_usernames)
        self.assertNotIn('sree', available_usernames)
        self.assertNotIn('other', busy_usernames)

    def test_availability_rejects_invalid_interval(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('get_faculty_availability'), {
            'date': '2026-10-28', 'start_time': '12:00', 'end_time': '11:00',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_faculty_search_returns_name_suggestions(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/faculty/search/?q=sre')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['username'], 'sree')

    def test_scheduling_meeting_creates_invitation_notification(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/scheduled-meetings/', {
            'title': 'Department planning',
            'date': '2027-02-01',
            'start_time': '10:00',
            'end_time': '11:00',
            'participant_usernames': ['other'],
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Notification.objects.filter(recipient=self.other_profile, meeting_id=response.data['id']).exists())

    def test_push_subscription_stores_encrypted_key_material(self):
        self.client.force_authenticate(user=self.user)
        subscription = {
            'endpoint': 'https://push.example.test/subscription/sree',
            'keys': {'p256dh': 'public-key-value', 'auth': 'auth-value'},
        }
        response = self.client.post('/api/push-subscriptions/', subscription, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        saved = PushSubscription.objects.get(endpoint=subscription['endpoint'])
        self.assertNotEqual(saved.p256dh, subscription['keys']['p256dh'])
        self.assertNotEqual(saved.auth, subscription['keys']['auth'])

        delete_response = self.client.delete('/api/push-subscriptions/', {'endpoint': subscription['endpoint']}, format='json')
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(PushSubscription.objects.filter(endpoint=subscription['endpoint']).exists())
