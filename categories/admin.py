from django.contrib import admin
from .models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'parent', 'similar_count')
    list_filter = ('parent',)
    search_fields = ('name',)
    autocomplete_fields = ['parent', 'similar_categories']

    def similar_count(self, obj):
        return obj.similar_categories.count()