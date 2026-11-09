from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [('faculty_calendar', '0008_scheduledmeeting_participants')]
    operations = [
        migrations.AddField(
            model_name='facultyprofile', name='is_department_head',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='AcademicEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=160)),
                ('description', models.TextField(blank=True)),
                ('date', models.DateField()),
                ('start_time', models.TimeField(blank=True, null=True)),
                ('end_time', models.TimeField(blank=True, null=True)),
                ('department', models.CharField(blank=True, max_length=100)),
                ('is_published', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('published_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='published_academic_events', to='faculty_calendar.facultyprofile')),
            ],
            options={'ordering': ['date', 'start_time', 'title']},
        ),
    ]
