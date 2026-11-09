from django.contrib.auth.models import User
from rest_framework import serializers
from .models import FacultyProfile, TimeTable, MeetingSlot


class UserSerializer(serializers.ModelSerializer):
    staff_code = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'staff_code', 'is_staff')

    def get_staff_code(self, obj):
        # Prefer the explicit staff ID; retain a fallback for legacy demo users.
        profile = getattr(obj, 'facultyprofile', None)
        if profile and profile.staff_id:
            return profile.staff_id
        username = (obj.username or '').strip()
        digits = ''.join(ch for ch in username if ch.isdigit())
        return f'MU-{digits[-3:]}' if len(digits) >= 3 else ''

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class FacultyProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    department_head = serializers.BooleanField(source='is_department_head', read_only=True)

    class Meta:
        model = FacultyProfile
        fields = ('id', 'staff_id', 'user', 'profile_picture', 'department', 'faculty_position', 'department_head')


class TimeTableSerializer(serializers.ModelSerializer):
    faculty = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = TimeTable
        fields = ('id', 'faculty', 'day', 'start_time', 'end_time', 'class_room')

    def validate(self, attrs):
        start_time = attrs.get('start_time', getattr(self.instance, 'start_time', None))
        end_time = attrs.get('end_time', getattr(self.instance, 'end_time', None))
        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError({'end_time': 'End time must be later than start time.'})
        return attrs


class MeetingSlotSerializer(serializers.ModelSerializer):
    faculty = serializers.PrimaryKeyRelatedField(read_only=True)
    faculty_name = serializers.CharField(source='faculty.user.username', read_only=True)

    class Meta:
        model = MeetingSlot
        fields = ('id', 'faculty', 'faculty_name', 'date', 'start_time', 'end_time', 'is_available')

    def validate(self, attrs):
        start_time = attrs.get('start_time', getattr(self.instance, 'start_time', None))
        end_time = attrs.get('end_time', getattr(self.instance, 'end_time', None))
        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError({'end_time': 'End time must be later than start time.'})
        return attrs
