from drf_spectacular.utils import extend_schema, OpenApiParameter, inline_serializer
from rest_framework import serializers, viewsets, status, decorators
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Category
from .serializers import CategoryDetailSerializer, CategorySerializer
from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 1000

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.select_related('parent').all().order_by('id')
    # serializer_class = CategorySerializer # no need for now as it will overflow
    def get_serializer_class(self):
        if self.action == 'retrieve':
            # Use the one that includes counts/details
            return CategoryDetailSerializer
        # Use the slim one for 'list', 'create', 'update', etc.
        return CategorySerializer

    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        # Optimization: Only load similarity IDs for the detail view
        # to avoid massive joins on the list view.
        if self.action == 'retrieve':
            return Category.objects.prefetch_related('similar_categories')
        return Category.objects.all().order_by('id')

    @extend_schema(summary="Get the full arbitrarily deep category tree")
    @decorators.action(detail=False, methods=['get'])
    def tree(self, request):
        """
        High-performance tree assembly. 
        Bypasses DRF Serializers to avoid Recursion 500s.
        """
        # 1. Fetch data leanly (No similarity prefetching here!)
        queryset = Category.objects.all().values('id', 'name', 'parent_id', 'description', 'image')
        
        # 2. Create a lookup map
        # We use a dict for O(1) access
        nodes = {item['id']: {**item, 'children': []} for item in queryset}
        
        roots = []
        for item_id, node in nodes.items():
            parent_id = node['parent_id']
            if parent_id is None:
                roots.append(node)
            else:
                # If the parent exists in our map, attach this node as a child
                if parent_id in nodes:
                    # Circular dependency guard: don't attach if it creates a loop
                    if parent_id != item_id:
                        nodes[parent_id]['children'].append(node)
                else:
                    # Parent ID exists but node doesn't (Orphan), treat as root
                    roots.append(node)

        return Response(roots)

    @extend_schema(
        summary="Move a category to a new parent",
        request=inline_serializer(
            name='MoveCategorySerializer',
            fields={'parent_id': serializers.IntegerField(allow_null=True)}
        ),
        responses={200: CategorySerializer}
    )
    @decorators.action(detail=True, methods=['patch'])
    def move(self, request, pk=None):
        category = self.get_object()
        category.parent_id = request.data.get('parent_id')
        category.save()
        return Response(CategorySerializer(category).data)

    @extend_schema(
        methods=['POST'],
        summary="Create a similarity link",
        request=inline_serializer(
            name='SimilarityCreateSerializer',
            fields={'target_id': serializers.IntegerField()}
        )
    )
    @extend_schema(
        methods=['DELETE'],
        summary="Remove a similarity link",
        request=inline_serializer(
            name='SimilarityDeleteSerializer',
            fields={'target_id': serializers.IntegerField()}
        )
    )
    @decorators.action(detail=True, methods=['post', 'delete'])
    def similarity(self, request, pk=None):
        category = self.get_object()
        target_id = request.data.get('target_id')
        target = get_object_or_404(Category, id=target_id)

        if request.method == 'POST':
            category.similar_categories.add(target)
            return Response({"status": "linked"}, status=status.HTTP_201_CREATED)
        
        if request.method == 'DELETE':
            category.similar_categories.remove(target)
            return Response({"status": "unlinked"}, status=status.HTTP_204_NO_CONTENT)