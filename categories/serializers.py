from rest_framework import serializers
from .models import Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'image', 'parent']

class BulkSimilaritySerializer(serializers.Serializer):
    # Accepts JSON: { "pairs": [[1, 2], [3, 4]] }
    pairs = serializers.ListField(
        child=serializers.ListField(child=serializers.IntegerField())
    )