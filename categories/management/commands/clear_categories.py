from django.core.management.base import BaseCommand
from django.db import connection
from categories.models import Category

class Command(BaseCommand):
    help = 'High-performance wipe of all categories and similarities using SQL TRUNCATE'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Skip confirmation prompt',
        )

    def handle(self, *args, **options):
        if not options['force']:
            confirm = input("This will RESTART all IDs and delete 200k+ records. Type 'yes' to proceed: ")
            if confirm.lower() != 'yes':
                self.stdout.write("Operation cancelled.")
                return

        self.stdout.write("Wiping database...")
        
        # We use RESTART IDENTITY to reset the ID counters to 1
        # CASCADE ensures the ManyToMany 'through' table is wiped as well
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE categories_category RESTART IDENTITY CASCADE;')
            
        self.stdout.write(self.style.SUCCESS("Database is clean. ID counters reset to 1."))