from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'timetable', views.TimeTableViewSet, basename='timetable')
router.register(r'meetings', views.MeetingSlotViewSet, basename='meetings')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.login_view, name='login'),
    path('holidays/', views.public_holidays, name='public-holidays'),
    path('logout/', views.logout_view, name='logout'),
    path('check-availability/', views.check_availability, name='check-availability'),
    path('get_all_entries/', views.get_all_entries, name='get_all_entries'),
    path('get_timetable/', views.get_timetable, name='get_timetable'),
    path('get_all_timetables/', views.get_all_timetables, name='get_all_timetables'),
    path('get_all_users_with_timetables/', views.get_all_users_with_timetables, name='get_all_users_with_timetables'),
    path('get_faculty_availability/', views.get_faculty_availability, name='get_faculty_availability'),
    path('faculty/search/', views.search_faculty, name='search-faculty'),
    path('faculty/available-slots/', views.faculty_date_slots, name='faculty-available-slots'),
    path('scheduled-meetings/', views.scheduled_meetings, name='scheduled-meetings'),
    path('scheduled-meetings/<int:meeting_id>/response/', views.meeting_response, name='meeting-response'),
    path('notifications/', views.notifications, name='notifications'),
    path('push-subscriptions/', views.push_subscriptions, name='push-subscriptions'),
    path('academic-events/', views.academic_events, name='academic-events'),
]
