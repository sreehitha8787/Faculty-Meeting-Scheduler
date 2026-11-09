from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [('faculty_calendar', '0005_reference_holidays')]

    operations = [
        migrations.CreateModel(
            name='ScheduledMeeting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=160)),
                ('agenda', models.TextField(blank=True)),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined'), ('cancelled', 'Cancelled')], default='pending', max_length=12)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('organizer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='organized_meetings', to='faculty_calendar.facultyprofile')),
            ],
            options={'ordering': ['date', 'start_time']},
        ),
        migrations.CreateModel(
            name='MeetingParticipant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response', models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined')], default='pending', max_length=10)),
                ('faculty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='faculty_calendar.facultyprofile')),
                ('meeting', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='faculty_calendar.scheduledmeeting')),
            ],
            options={'unique_together': {('meeting', 'faculty')}},
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=255)),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('meeting', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='faculty_calendar.scheduledmeeting')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='faculty_calendar.facultyprofile')),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
