from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('faculty_calendar', '0007_faculty_position')]

    operations = [
        migrations.AddField(
            model_name='scheduledmeeting',
            name='participants',
            field=models.ManyToManyField(
                related_name='invited_meetings',
                through='faculty_calendar.MeetingParticipant',
                to='faculty_calendar.facultyprofile',
            ),
        ),
    ]
