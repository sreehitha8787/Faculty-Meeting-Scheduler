from datetime import date, time, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faculty_calendar.models import FacultyProfile, TimeTable, MeetingSlot, PublicHoliday
from faculty_calendar.holiday_data import REFERENCE_HOLIDAYS

User = get_user_model()

# Entirely fictional demo data for local development; these are not actual MU staff.
# Staff IDs are MU-101 through MU-150; usernames include the name and 3-digit code.
STAFF = [
    (101, "Ananya", "Rao", "Computer Science and Engineering"),
    (102, "Arjun", "Reddy", "Computer Science and Engineering"),
    (103, "Meera", "Krishnan", "Electronics and Communication Engineering"),
    (104, "Karthik", "Varma", "Electrical and Electronics Engineering"),
    (105, "Ishita", "Sharma", "Mathematics"),
    (106, "Rahul", "Nair", "Physics"),
    (107, "Kavya", "Iyer", "Mechanical Engineering"),
    (108, "Aditya", "Menon", "Civil Engineering"),
    (109, "Sana", "Khan", "Management Studies"),
    (110, "Vikram", "Rao", "Computer Science and Engineering"),
    (111, "Pooja", "Reddy", "Electronics and Communication Engineering"),
    (112, "Nikhil", "Patel", "Mathematics"),
    (113, "Diya", "Thomas", "Physics"),
    (114, "Rohan", "Desai", "Mechanical Engineering"),
    (115, "Priya", "Naidu", "Civil Engineering"),
    (116, "Aarav", "Kulkarni", "Computer Science and Engineering"),
    (117, "Aadhya", "Chowdhury", "Computer Science and Engineering"),
    (118, "Ishaan", "Kapoor", "Electronics and Communication Engineering"),
    (119, "Anika", "Joshi", "Electrical and Electronics Engineering"),
    (120, "Dev", "Bhatia", "Mathematics"),
    (121, "Mira", "Pillai", "Physics"),
    (122, "Siddharth", "Shah", "Mechanical Engineering"),
    (123, "Nandini", "Murthy", "Civil Engineering"),
    (124, "Varun", "Saxena", "Management Studies"),
    (125, "Ritika", "Das", "Computer Science and Engineering"),
    (126, "Harish", "Gopal", "Computer Science and Engineering"),
    (127, "Tanvi", "Deshmukh", "Electronics and Communication Engineering"),
    (128, "Manav", "Chandra", "Electrical and Electronics Engineering"),
    (129, "Keerthi", "Rajan", "Mathematics"),
    (130, "Abhinav", "Mishra", "Physics"),
    (131, "Shreya", "Bose", "Mechanical Engineering"),
    (132, "Pranav", "Shetty", "Civil Engineering"),
    (133, "Lavanya", "Rao", "Management Studies"),
    (134, "Yash", "Malhotra", "Computer Science and Engineering"),
    (135, "Sanjana", "Pillai", "Computer Science and Engineering"),
    (136, "Akash", "Verma", "Electronics and Communication Engineering"),
    (137, "Rhea", "Fernandes", "Electrical and Electronics Engineering"),
    (138, "Sai", "Krishna", "Mathematics"),
    (139, "Neha", "Srinivasan", "Physics"),
    (140, "Amit", "Joshi", "Mechanical Engineering"),
    (141, "Bhavana", "Reddy", "Civil Engineering"),
    (142, "Ritesh", "Gupta", "Management Studies"),
    (143, "Anirudh", "Kumar", "Computer Science and Engineering"),
    (144, "Swathi", "Prasad", "Computer Science and Engineering"),
    (145, "Deepak", "Nambiar", "Electronics and Communication Engineering"),
    (146, "Aishwarya", "Menon", "Electrical and Electronics Engineering"),
    (147, "Madhav", "Rao", "Mathematics"),
    (148, "Pallavi", "Shukla", "Physics"),
    (149, "Gautam", "Sethi", "Mechanical Engineering"),
    (150, "Charitha", "Naidu", "Civil Engineering")
]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
SLOTS = [(time(9, 0), time(10, 0)), (time(10, 15), time(11, 15)),
         (time(11, 30), time(12, 30)), (time(13, 30), time(14, 30)),
         (time(14, 45), time(15, 45))]


def staff_username(first, last, number):
    return f"{first}{last}{number}".lower()


class Command(BaseCommand):
    help = "Create 50 fictional MU Staff Calendar demo users, timetables and meeting slots."

    def add_arguments(self, parser):
        parser.add_argument('--reset-demo', action='store_true', help='Delete generated demo users and their related records, then recreate them.')

    def handle(self, *args, **options):
        usernames = [staff_username(first, last, number) for number, first, last, _ in STAFF]
        # Include usernames from the earlier 15-record demo version for a clean migration.
        legacy_usernames = [f'mu{n}' for n in range(101, 116)] + [f'{first}.{last}{number}'.lower() for number, first, last, _ in STAFF]
        if options['reset_demo']:
            old_users = User.objects.filter(username__in=usernames + legacy_usernames)
            old_profiles = FacultyProfile.objects.filter(user__in=old_users)
            MeetingSlot.objects.filter(faculty__in=old_profiles).delete()
            TimeTable.objects.filter(faculty__in=old_profiles).delete()
            old_profiles.delete()
            old_users.delete()

        created_users = created_tables = created_meetings = 0
        profiles = []
        for number, first, last, department in STAFF:
            username = staff_username(first, last, number)
            user, created = User.objects.get_or_create(username=username, defaults={
                'first_name': first, 'last_name': last,
                'email': f'{username}@example.test', 'is_active': True,
            })
            if created:
                user.set_password('Demo@12345')
                user.save()
                created_users += 1
            profile, _ = FacultyProfile.objects.get_or_create(user=user, defaults={
                'staff_id': f'MU-{number}',
                'department': department,
                'profile_picture': '',
            })
            # Keep the generated staff ID and department consistent on reruns.
            changed = False
            if profile.staff_id != f'MU-{number}':
                profile.staff_id = f'MU-{number}'; changed = True
            if profile.department != department:
                profile.department = department; changed = True
            if profile.is_department_head != (number == 101):
                profile.is_department_head = number == 101; changed = True
            if changed:
                profile.save()
            profiles.append((number, profile))

        for number, profile in profiles:
            for idx, day in enumerate(DAYS):
                start, end = SLOTS[(number + idx) % len(SLOTS)]
                _, created = TimeTable.objects.get_or_create(
                    faculty=profile, day=day, start_time=start,
                    defaults={'end_time': end, 'class_room': ('ABC'[number % 3] + '-' + str(100 + (number % 20)))},
                )
                if created:
                    created_tables += 1

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

        today = date.today()
        next_monday = today + timedelta(days=(7 - today.weekday()) % 7)
        for idx, (number, profile) in enumerate(profiles):
            meeting_date = next_monday + timedelta(days=idx % 10)
            start, end = SLOTS[idx % len(SLOTS)]
            _, created = MeetingSlot.objects.get_or_create(
                faculty=profile, date=meeting_date, start_time=start,
                defaults={'end_time': end, 'is_available': (idx % 3 == 0)},
            )
            if created:
                created_meetings += 1

        self.stdout.write(self.style.SUCCESS(
            f'Demo seed complete. Staff records: {len(STAFF)}; recurring weekly timetable entries: {TimeTable.objects.count()}; new users: {created_users}; timetable entries added: {created_tables}; meeting slots added: {created_meetings}; reference holidays: {PublicHoliday.objects.filter(date__gte="2027-01-01", date__lte="2028-01-31").count()}.'
        ))
        self.stdout.write('Staff IDs: MU-101 through MU-150.')
        self.stdout.write('Usernames contain letters and digits only, e.g. ananyarao101.')
        self.stdout.write('Shared demo password for newly created users: Demo@12345')
        self.stdout.write(self.style.WARNING('Fictional development-only data. Do not use demo credentials in production.'))
