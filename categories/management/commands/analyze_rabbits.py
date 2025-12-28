from django.core.management.base import BaseCommand
from categories.models import Category
import networkx as nx

class Command(BaseCommand):
    help = 'Analyzes Rabbit Islands and Longest Rabbit Holes'

    def handle(self, *args, **options):
        # 1. Fetch Data (Optimized)
        # We only need ID pairs. Using values_list is much faster than ORM objects.
        ThroughModel = Category.similar_categories.through
        
        self.stdout.write("Fetching similarity graph...")
        # iterator() prevents loading all 200k rows into RAM at once
        edges = ThroughModel.objects.values_list('from_category_id', 'to_category_id').iterator()
        
        all_ids = Category.objects.values_list('id', flat=True)

        # 2. Build Graph
        # NetworkX is C-optimized. 200k edges takes <100ms.
        G = nx.Graph()
        G.add_nodes_from(all_ids)
        G.add_edges_from(edges)

        # 3. Analyze Islands (Connected Components)
        # Generator for memory efficiency
        components = list(nx.connected_components(G))
        self.stdout.write(f"Found {len(components)} Rabbit Islands.")

        # Print Islands
        for i, island in enumerate(components):
            if len(island) > 1:
                # Limit output for sanity
                sample = list(island)[:5]
                self.stdout.write(f"  Island {i+1} Size: {len(island)} nodes. Examples: {sample}")

        # 4. Find The "Deepest" Rabbit Hole (Graph Diameter)
        # Definition: The longest shortest-path in the graph.
        
        longest_path = []
        max_length = 0

        self.stdout.write("Calculating Longest Rabbit Hole...")

        for island in components:
            if len(island) < 2: continue
            
            # Optimization: If this island is smaller than our current max_length, skip it.
            # (Diameter cannot exceed node count)
            if len(island) <= max_length: continue

            subgraph = G.subgraph(island)
            
            # Calculate eccentricity (max distance) for all nodes
            # This is O(V*E) but efficient enough for 2000 nodes.
            try:
                # 'extrema_bounding' is a NetworkX heuristic for diameter
                diameter = nx.diameter(subgraph)
                
                if diameter > max_length:
                    # We found a better candidate island, now we need the ACTUAL path.
                    # NetworkX doesn't give the path with `diameter()`, only the length.
                    # We run BFS to find the specific nodes.
                    
                    # Compute all shortest paths (Heavy op, but done only on candidate islands)
                    all_paths = dict(nx.all_pairs_shortest_path(subgraph))
                    
                    for source, targets in all_paths.items():
                        for target, path in targets.items():
                            if len(path) - 1 == diameter: # -1 because path includes start node
                                max_length = diameter
                                longest_path = path
                                break # Found one max path in this island, move on
            except Exception as e:
                self.stdout.write(f"Skipping island due to error: {e}")

        # 5. Output Result
        if longest_path:
            # Fetch names in one Batch Query
            cats = Category.objects.in_bulk(longest_path)
            names = [cats[uid].name for uid in longest_path]
            
            self.stdout.write(self.style.SUCCESS(f"\nLongest Rabbit Hole found!"))
            self.stdout.write(f"Length: {max_length} hops")
            self.stdout.write(f"Path: {' -> '.join(names)}")
        else:
            self.stdout.write("No rabbit holes found (no similar categories).")