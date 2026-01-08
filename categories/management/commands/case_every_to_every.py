import io
import time
import itertools
from django.core.management.base import BaseCommand
from django.db import connection
from categories.models import Category

class Command(BaseCommand):
    help = 'Generates a Fully Connected Graph (The Black Hole)'

    def handle(self, *args, **options):
        N_NODES = 2000  # Generates ~2 Million edges (N*(N-1)/2)
        
        # 1. Clean Slate
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE categories_category RESTART IDENTITY CASCADE")

        self.stdout.write(f"Creating {N_NODES} nodes...")
        start_time = time.time()

        # 2. Create Nodes
        cats = [Category(name=f"Node_{i}") for i in range(N_NODES)]
        Category.objects.bulk_create(cats, batch_size=5000)
        
        ids = list(Category.objects.values_list('id', flat=True))

        # 3. Stream 2 Million Edges (Memory Efficient)
        self.stdout.write(f"Generating Complete Graph ({len(ids)*(len(ids)-1)//2} edges)...")
        
        # Using a generator + string buffer to avoid holding 2M tuples in RAM
        def generate_csv():
            for a, b in itertools.combinations(ids, 2):
                yield f"{a}\t{b}\n"

        # 4. Direct Copy into Postgres
        class StringIteratorIO(io.TextIOBase):
            def __init__(self, iter):
                self._iter = iter
                self._buff = ''
            def read(self, n=None):
                while not self._buff:
                    try:
                        self._buff = next(self._iter)
                    except StopIteration:
                        return ''
                ret = self._buff[:n]
                self._buff = self._buff[n:]
                return ret

        with connection.cursor() as cursor:
            data_iter = StringIteratorIO(generate_csv())
            cursor.copy_from(
                data_iter, 
                'categories_category_similar_categories', 
                columns=('from_category_id', 'to_category_id')
            )
        
        connection.commit()

        self.stdout.write(self.style.SUCCESS(f"Black Hole Created in {time.time() - start_time:.2f}s"))