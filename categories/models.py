from django.db import models
from django.db import transaction
from rest_framework.exceptions import ValidationError

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
        related_name='children',
    )

    # Similarity: Symmetrical M2M
    similar_categories = models.ManyToManyField(
        'self', 
        blank=True, 
        symmetrical=True
    )

    def clean(self):
        # 1. Self-parenting guard
        if self.parent_id and self.id == self.parent_id:
            raise ValidationError("A category cannot be its own parent.")
        
        # 2. Circular dependency guard (for existing objects)
        if self.id and self.parent:
            curr = self.parent
            while curr is not None:
                if curr.id == self.id:
                    raise ValidationError("Circular dependency detected in category tree.")
                curr = curr.parent

    @transaction.atomic
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs) # This will lock the table for writes

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"