from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, null=True)
    image = models.CharField(max_length=255, blank=True, null=True)
    
    # 1. Tree Structure (Adjacency List)
    # A category links to its parent. If parent is null, it's a root.
    parent = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='children',
        db_index=True  # Important for tree queries
    )

    # 2. Similarity (Graph)
    # 'symmetrical=True' means if A is similar to B, Django sees B as similar to A.
    similar_categories = models.ManyToManyField(
        'self', 
        blank=True, 
        symmetrical=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"