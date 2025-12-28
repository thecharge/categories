import io
import time
import random
from django.core.management.base import BaseCommand
from django.db import connection
from categories.models import Category

class Command(BaseCommand):
    def handle(self, *args, **options):
        # ... (Wipe and Category creation logic stays the same) ...

        self.stdout.write("Generating 200,000 unique similarity pairs...")
        start_time = time.time()
        
        ids = list(Category.objects.values_list('id', flat=True))
        pairs = set()
        while len(pairs) < 200000:
            a, b = random.sample(ids, 2)
            pairs.add(tuple(sorted((a, b))))

        # format data for psycopg2 copy_from (tab-separated)
        buf = io.StringIO()
        for a, b in pairs:
            buf.write(f"{a}\t{b}\n")
        buf.seek(0)

        # Access the raw connection and cursor
        with connection.cursor() as cursor:
            # Under the hood, Django's cursor wraps the psycopg2 cursor
            raw_cursor = cursor.cursor
            raw_cursor.copy_from(buf, 'categories_category_similar_categories', 
                               columns=('from_category_id', 'to_category_id'))
        
        # Explicit commit is required when using raw cursor
        connection.commit()

        elapsed = time.time() - start_time
        self.stdout.write(self.style.SUCCESS(f"Populated 200k edges in {elapsed:.2f}s"))