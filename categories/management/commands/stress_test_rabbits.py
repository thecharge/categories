import io
import time
import random
from django.core.management.base import BaseCommand
from django.db import connection
from categories.models import Category

class Command(BaseCommand):
    help = 'Generates 2k tree and 200k edges using Level-order Bulk Creation'

    def handle(self, *args, **options):
        # 1. Clean Slate
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE categories_category RESTART IDENTITY CASCADE")

        self.stdout.write("Building 2,000 node hierarchy in levels...")
        start_time = time.time()

        # 2. Level-order Creation
        # Level 0 (Roots)
        roots = [Category(name=f"Root_{i}") for i in range(50)]
        Category.objects.bulk_create(roots)
        
        all_created_cats = list(Category.objects.all())
        current_level_parents = all_created_cats[:]
        
        target_total = 2000
        while len(all_created_cats) < target_total:
            batch = []
            # Create children for the parents of the previous level
            for parent in current_level_parents:
                if len(all_created_cats) + len(batch) >= target_total:
                    break
                
                # Each parent gets 1-3 children to build a natural tree
                for c_idx in range(random.randint(1, 3)):
                    if len(all_created_cats) + len(batch) < target_total:
                        batch.append(Category(
                            name=f"Cat_{len(all_created_cats) + len(batch)}",
                            parent=parent
                        ))
            
            # Save this level
            new_nodes = Category.objects.bulk_create(batch)
            all_created_cats.extend(new_nodes)
            current_level_parents = new_nodes # This level becomes parents for the next

        ids = [c.id for c in all_created_cats]
        self.stdout.write(f"Tree built in {time.time() - start_time:.2f}s")

        # 3. Fast Edge Generation (Similarity Graph)
        self.stdout.write("Generating 200,000 similarity pairs...")
        sim_start = time.time()
        
        pairs = set()
        while len(pairs) < 200000:
            a, b = random.sample(ids, 2)
            pairs.add(tuple(sorted((a, b))))

        buf = io.StringIO()
        for a, b in pairs:
            buf.write(f"{a}\t{b}\n")
        buf.seek(0)

        # 4. Psycopg2 Copy (Direct SQL)
        with connection.cursor() as cursor:
            # 1. Create a temp table to hold the new pairs
            cursor.execute("CREATE TEMP TABLE temp_similarities (f_id INT, t_id INT) ON COMMIT DROP")
            connection.commit()
        
        with connection.cursor() as cursor:
            # 2. Use copy_from to load the temp table fast
            cursor.copy_from(buf, 'temp_similarities', columns=('f_id', 't_id'))
            
            # 3. Idempotent move from Temp to Real table
            cursor.execute("""
                INSERT INTO categories_category_similar_categories (from_category_id, to_category_id)
                SELECT f_id, t_id FROM temp_similarities
                ON CONFLICT DO NOTHING
            """)
            connection.commit()