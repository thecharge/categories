from django.core.management.base import BaseCommand
from categories.models import Category
import networkx as nx

class Command(BaseCommand):
    help = 'Analyzes Rabbit Islands and Holes'

    def handle(self, *args, **options):
        self.stdout.write("Fetching Graph Data...")
        
        # 1. Fetch Edges directly from the Through table (Fastest)
        ThroughModel = Category.similar_categories.through
        links = ThroughModel.objects.values_list('from_category_id', 'to_category_id')
        
        # 2. Build Graph using NetworkX
        G = nx.Graph()
        G.add_edges_from(links)
        
        # Add all IDs (even those with no connections)
        all_ids = Category.objects.values_list('id', flat=True)
        G.add_nodes_from(all_ids)

        self.stdout.write(f"Graph Built: {G.number_of_nodes()} categories.")

        # 3. Analyze Islands (Connected Components)
        islands = list(nx.connected_components(G))
        self.stdout.write(self.style.SUCCESS(f"Found {len(islands)} Rabbit Islands."))

        # 4. Find Longest Rabbit Hole (Diameter)
        max_len = 0
        longest_path = []

        # Iterate through every island to find the longest path within it
        for island in islands:
            if len(island) < 2: continue
            
            subgraph = G.subgraph(island)
            
            # Calculate shortest path between ALL pairs in this island
            # Then find the longest of those shortest paths
            try:
                paths = dict(nx.all_pairs_shortest_path(subgraph))
                for src, targets in paths.items():
                    for dest, path in targets.items():
                        if len(path) > max_len:
                            max_len = len(path)
                            longest_path = path
            except Exception:
                pass

        if longest_path:
            # Fetch names for the output
            cats = Category.objects.in_bulk(longest_path)
            names = [cats[uid].name for uid in longest_path if uid in cats]
            
            self.stdout.write(self.style.WARNING(f"\nLongest Rabbit Hole ({max_len-1} hops):"))
            self.stdout.write(" -> ".join(names))