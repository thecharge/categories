from rest_framework import viewsets, status, decorators
from rest_framework.response import Response
from .models import Category
from .serializers import CategorySerializer, BulkSimilaritySerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer

    @decorators.action(detail=False, methods=['get'])
    def tree(self, request):
        """
        Fetches all categories (1 DB query) and assembles them into a nested tree.
        """
        # 1. Fetch data leanly
        categories = Category.objects.values('id', 'name', 'parent_id')
        
        # 2. Build a lookup dictionary
        # Each node has an empty 'children' list initially
        cat_map = {
            c['id']: {'id': c['id'], 'name': c['name'], 'children': []} 
            for c in categories
        }
        
        roots = []

        # 3. Assemble the tree
        for c in categories:
            node = cat_map[c['id']]
            parent_id = c['parent_id']
            
            if parent_id and parent_id in cat_map:
                # Add self to parent's children
                cat_map[parent_id]['children'].append(node)
            else:
                # No parent? It's a root
                roots.append(node)
        
        return Response(roots)

    @decorators.action(detail=False, methods=['post'])
    def bulk_similarity(self, request):
        """
        Bulk adds similarity connections.
        """
        serializer = BulkSimilaritySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pairs = serializer.validated_data['pairs']

        # Access the auto-generated through table
        ThroughModel = Category.similar_categories.through
        links = []
        seen = set()

        for a, b in pairs:
            if a == b: continue
            # Sort IDs to prevent duplicates (A-B vs B-A)
            low, high = sorted((a, b))
            if (low, high) not in seen:
                links.append(ThroughModel(from_category_id=low, to_category_id=high))
                seen.add((low, high))

        # Bulk insert, ignoring conflicts if they already exist
        ThroughModel.objects.bulk_create(links, ignore_conflicts=True)

        return Response({"status": "success", "pairs_added": len(links)})