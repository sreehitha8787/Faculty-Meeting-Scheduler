from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('faculty_calendar', '0003_facultyprofile_staff_id')]
    operations = [migrations.CreateModel(name='PublicHoliday', fields=[
        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        ('date', models.DateField(unique=True)),
        ('name', models.CharField(max_length=160)),
        ('region', models.CharField(default='All India', max_length=80)),
        ('source', models.CharField(blank=True, max_length=255)),
        ('is_active', models.BooleanField(default=True)),
    ], options={'ordering': ['date']} )]
