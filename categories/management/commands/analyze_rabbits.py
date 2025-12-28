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

        # 3. Find the Longest Rabbit Hole
        if islands:
            largest_island = max(islands, key=len)
            S = G.subgraph(largest_island)
            
            # 2-Pass BFS (Extreme point to extreme point)
            # This is O(V+E) - lightning fast even for huge graphs
            source_node = list(largest_island)[0]
            
            # Pass 1: Find node u furthest from a random point
            u = max(nx.single_source_shortest_path_length(S, source_node).items(), key=lambda x: x[1])[0]
            
            # Pass 2: Find node v furthest from u
            distances = nx.single_source_shortest_path_length(S, u)
            v, max_dist = max(distances.items(), key=lambda x: x[1])
            
            path = nx.shortest_path(S, source=u, target=v)
            
            # Resolve names for output
            names = Category.objects.in_bulk(path)
            path_names = [names[nid].name for nid in path]

            self.stdout.write(self.style.SUCCESS(f"\nLongest Rabbit Hole found in {time.time() - start_time:.2f}s"))
            self.stdout.write(f"Hole: {' -> '.join(path_names)} ({max_dist} steps)")