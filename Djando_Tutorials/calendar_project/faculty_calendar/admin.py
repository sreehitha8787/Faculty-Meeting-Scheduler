from django.contrib import admin
from .models import FacultyProfile, TimeTable, MeetingSlot, PublicHoliday, ScheduledMeeting, Notification, AcademicEvent

@admin.register(FacultyProfile)
class FacultyProfileAdmin(admin.ModelAdmin):
    list_display = ('staff_id', 'user', 'department', 'faculty_position', 'is_department_head')
    search_fields = ('staff_id', 'user__username', 'user__first_name', 'user__last_name')

@admin.register(TimeTable)
class TimeTableAdmin(admin.ModelAdmin):
    list_display = ('faculty', 'day', 'start_time', 'end_time', 'class_room')
    list_filter = ('day',)

@admin.register(MeetingSlot)
class MeetingSlotAdmin(admin.ModelAdmin):
    list_display = ('faculty', 'date', 'start_time', 'end_time', 'is_available')
    list_filter = ('date', 'is_available')

@admin.register(PublicHoliday)
class PublicHolidayAdmin(admin.ModelAdmin):
    list_display = ('date', 'name', 'region', 'is_active')
    list_filter = ('region', 'is_active')
    search_fields = ('name',)

@admin.register(ScheduledMeeting)
class ScheduledMeetingAdmin(admin.ModelAdmin):
    list_display = ('title', 'organizer', 'date', 'start_time', 'end_time', 'status')
    list_filter = ('status', 'date')
    search_fields = ('title', 'organizer__user__username')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'message', 'is_read', 'created_at')
    list_filter = ('is_read',)
    search_fields = ('recipient__user__username', 'message')

@admin.register(AcademicEvent)
class AcademicEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'department', 'published_by', 'is_published')
    list_filter = ('department', 'is_published', 'date')
    search_fields = ('title', 'description')
