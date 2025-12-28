from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    
    # Tree: Adjacency list
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children'
    )

    # Similarity: Symmetrical M2M
    similar_categories = models.ManyToManyField(
        'self', 
        blank=True, 
        symmetrical=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"