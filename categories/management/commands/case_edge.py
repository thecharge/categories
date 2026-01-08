import io
import time
from django.core.management.base import BaseCommand
from django.db import connection
from categories.models import Category

class Command(BaseCommand):
    help = 'Generates The Logic Edge: A Massive Star vs A Long Snake'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE categories_category RESTART IDENTITY CASCADE")

        self.stdout.write("Generating Edge Topology...")
        start_time = time.time()
        buf = io.StringIO()

        ### ISLAND 1: THE MASSIVE STAR (10,000 nodes, Diameter = 2) ###
        # Center Node
        center = Category.objects.create(name="Star_Center")
        
        # 10k Orbiters
        satellites = [Category(name=f"Sat_{i}") for i in range(10000)]
        Category.objects.bulk_create(satellites)
        
        # Connect all satellites to Center
        # This makes a HUGE island (10,001 nodes)
        sat_ids = Category.objects.filter(name__startswith="Sat_").values_list('id', flat=True)
        for sid in sat_ids:
            buf.write(f"{center.id}\t{sid}\n")

        
        ### ISLAND 2: THE SNAKE (100 nodes, Diameter = 99) ###
        # This is a small island (100 nodes)
        snake_nodes = [Category(name=f"Snake_{i}") for i in range(100)]
        created_snake = Category.objects.bulk_create(snake_nodes)
        
        # Connect 0->1->2->3...
        for i in range(len(created_snake) - 1):
            u = created_snake[i].id
            v = created_snake[i+1].id
            buf.write(f"{u}\t{v}\n")

        # Flush to DB
        buf.seek(0)
        with connection.cursor() as cursor:
            cursor.copy_from(
                buf, 
                'categories_category_similar_categories', 
                columns=('from_category_id', 'to_category_id')
            )
        connection.commit()

        self.stdout.write(self.style.SUCCESS(f"Edge Set in {time.time() - start_time:.2f}s"))
        self.stdout.write("Test your analysis script now.")
        self.stdout.write("If it returns 'Star_Center' -> You FAILED (Caught by size heuristic).")
        self.stdout.write("If it returns 'Snake_0' -> You PASSED (Correctly checked all islands).")