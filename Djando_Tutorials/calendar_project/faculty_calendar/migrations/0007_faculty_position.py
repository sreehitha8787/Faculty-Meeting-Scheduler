from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('faculty_calendar', '0006_meetings_notifications')]

    operations = [
        migrations.AddField(
            model_name='facultyprofile',
            name='faculty_position',
            field=models.CharField(default='Faculty member', max_length=120),
        ),
    ]
