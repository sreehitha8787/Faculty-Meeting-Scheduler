from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faculty_calendar', '0002_rename_subject_timetable_class_room'),
    ]

    operations = [
        migrations.AddField(
            model_name='facultyprofile',
            name='staff_id',
            field=models.CharField(blank=True, max_length=10, null=True, unique=True),
        ),
    ]
