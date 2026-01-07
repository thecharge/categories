from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # 1. OPTIMIZED LIST VIEW
    list_display = ('name_with_uuid', 'parent_link', 'similarity_count', 'is_root')
    list_select_related = ('parent',)  # Prevents N+1 queries for parents
    
    # 2. SEARCH & FILTERING (Critical for UUIDs)
    # Allows pasting a full UUID or typing a name
    search_fields = ('id', 'name')
    list_filter = ('parent',) # Simple filter to find roots (parent=None)

    # 3. PERFORMANCE WIDGETS (The Anti-Crash Fix)
    # Uses AJAX to search for parents/similarities instead of loading 200k items
    autocomplete_fields = ['parent', 'similar_categories']
    
    # 4. READ-ONLY FIELDS
    # You cannot edit a UUID once created
    readonly_fields = ('id', 'created_display')

    # --- CUSTOM COLUMNS ---

    def get_queryset(self, request):
        """
        Annotate count efficiently so we can sort by 'popularity' (connections)
        """
        qs = super().get_queryset(request)
        return qs.annotate(sim_count=Count('similar_categories'))

    @admin.display(description="Category (UUID)", ordering='name')
    def name_with_uuid(self, obj):
        """Displays Name + tiny UUID for easy ID checks"""
        return format_html(
            "<b>{}</b><br/><span style='color: #888; font-size: 10px;'>{}</span>",
            obj.name,
            str(obj.id)
        )

    @admin.display(description="Parent", ordering='parent__name')
    def parent_link(self, obj):
        """Clickable link to the parent category"""
        if not obj.parent:
            return "-"
        return format_html(
            '<a href="/admin/categories/category/{}/change/">{}</a>',
            obj.parent.id,
            obj.parent.name
        )

    @admin.display(description="Similar Links", ordering='sim_count')
    def similarity_count(self, obj):
        """Shows count of edges. Click to view the raw list."""
        count = obj.sim_count
        if count > 100:
            style = "color: red; font-weight: bold;"
        elif count > 0:
            style = "color: green;"
        else:
            style = "color: #ccc;"
            
        return format_html(
            '<span style="{}">{} links</span>',
            style, count
        )

    @admin.display(boolean=True, description="Is Root")
    def is_root(self, obj):
        return obj.parent is None

    @admin.display(description="Created ID")
    def created_display(self, obj):
        return obj.id