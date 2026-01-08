import networkx as nx
import time
from django.core.management.base import BaseCommand
from django.db import connection
from categories.models import Category

class Command(BaseCommand):
    def handle(self, *args, **options):
        start_time = time.time()

        # 1. Load Graph (Streamed)
        with connection.cursor() as cursor:
            cursor.execute("SELECT from_category_id, to_category_id FROM categories_category_similar_categories")
            G = nx.from_edgelist(cursor.fetchall())

        # 2. Identify Islands
        islands = list(nx.connected_components(G))
        self.stdout.write(f"Islands: {len(islands)}")

        global_max_dist = 0
        best_path = []

       # 3. Checking each island
        for island in islands:
            S = G.subgraph(island)
            source_node = list(island)[0]

            # Pass 1
            u = max(nx.single_source_shortest_path_length(S, source_node).items(), key=lambda x: x[1])[0]
            
            # Pass 2
            distances = nx.single_source_shortest_path_length(S, u)
            v, max_dist = max(distances.items(), key=lambda x: x[1])
            
            if max_dist > global_max_dist:
                global_max_dist = max_dist
                best_path = nx.shortest_path(S, source=u, target=v)

        names = Category.objects.in_bulk(best_path)
        path_names = [names[nid].name for nid in best_path]
        self.stdout.write(self.style.SUCCESS(f"\nLongest Rabbit Hole found in {time.time() - start_time:.2f}s"))
        self.stdout.write(f"Hole: {' -> '.join(path_names)} ({max_dist} steps)")