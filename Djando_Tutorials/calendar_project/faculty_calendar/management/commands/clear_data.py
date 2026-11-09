from django.core.management.base import BaseCommand
from faculty_calendar.models import FacultyProfile, TimeTable, MeetingSlot

class Command(BaseCommand):
    help = 'Clear data from FacultyProfile, TimeTable, and MeetingSlot tables'

    def handle(self, *args, **kwargs):
        TimeTable.objects.all().delete()
        MeetingSlot.objects.all().delete()
        FacultyProfile.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Data cleared successfully!'))
