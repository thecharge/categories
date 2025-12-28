from rest_framework import serializers
from .models import Category

class CategorySerializer(serializers.ModelSerializer):
    """Used for Lists: Fast and Slim"""
    class Meta:
        model = Category
        fields = ['id', 'name', 'parent']

class CategoryDetailSerializer(serializers.ModelSerializer):
    """Used for Retrieve: Detailed with Similarities"""
    similar_count = serializers.IntegerField(source='similar_categories.count', read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'image', 'parent', 'similar_count']