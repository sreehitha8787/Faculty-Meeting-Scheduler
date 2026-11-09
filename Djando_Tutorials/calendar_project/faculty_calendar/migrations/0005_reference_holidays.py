from django.db import migrations

from faculty_calendar.holiday_data import REFERENCE_HOLIDAYS


def add_reference_holidays(apps, schema_editor):
    PublicHoliday = apps.get_model('faculty_calendar', 'PublicHoliday')
    for holiday_date, name, source in REFERENCE_HOLIDAYS:
        PublicHoliday.objects.update_or_create(
            date=holiday_date,
            defaults={
                'name': name,
                'region': 'Telangana, India',
                'source': source,
                'is_active': True,
            },
        )


class Migration(migrations.Migration):
    dependencies = [('faculty_calendar', '0004_publicholiday')]

    operations = [migrations.RunPython(add_reference_holidays, migrations.RunPython.noop)]
