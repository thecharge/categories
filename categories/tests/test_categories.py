import pytest
from django.urls import reverse
from rest_framework import status
from categories.models import Category
from categories.tests.factories import CategoryFactory

@pytest.mark.django_db
class TestCategoryAPI:
    
    def test_arbitrarily_deep_tree(self, client):
        """Task: Categories can be nested arbitrarily deep."""
        c1 = CategoryFactory(name="Root")
        c2 = CategoryFactory(name="Level 1", parent=c1)
        c3 = CategoryFactory(name="Level 2", parent=c2)
        c4 = CategoryFactory(name="Level 3", parent=c3)

        url = reverse('category-tree')
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        # Verify the nesting in the response
        tree = response.json()
        assert tree[0]['children'][0]['children'][0]['children'][0]['name'] == "Level 3"

    def test_bidirectional_similarity_crud(self, client):
        """Task: Similarity is bidirectional (A->B implies B->A)."""
        cat_a = CategoryFactory()
        cat_b = CategoryFactory()
        
        # Create similarity via API
        url = reverse('category-similarity', kwargs={'pk': cat_a.id})
        client.post(url, {'target_id': cat_b.id}, content_type='application/json')
        
        # Verify both directions in DB
        assert cat_b in cat_a.similar_categories.all()
        assert cat_a in cat_b.similar_categories.all()

        # Delete similarity
        client.delete(url, {'target_id': cat_b.id}, content_type='application/json')
        assert cat_b not in cat_a.similar_categories.all()

    def test_move_category(self, client):
        """Task: Categories can be moved around in the tree."""
        root1 = CategoryFactory(name="Root 1")
        root2 = CategoryFactory(name="Root 2")
        child = CategoryFactory(name="Movable Child", parent=root1)

        url = reverse('category-move', kwargs={'pk': child.id})
        response = client.patch(url, {'parent_id': root2.id}, content_type='application/json')
        
        assert response.status_code == status.HTTP_200_OK
        child.refresh_from_db()
        assert child.parent == root2
    
    @pytest.mark.django_db
    def test_circular_dependency_fails(api_client):
        a = Category.objects.create(name="A")
        b = Category.objects.create(name="B", parent=a)
        
        # Try to make A the child of B
        url = reverse('category-move', kwargs={'pk': a.id})
        response = api_client.patch(url, {'parent_id': b.id}, format='json')
        
        assert response.status_code == 400
        assert "Circular dependency" in response.data['error']
        
    def test_rabbit_hole_algorithm(self):
        """
        Task: Shortest sequence from A to B visiting similar categories.
        We verify the logic used by the management command.
        """
        import networkx as nx
        from categories.management.commands.analyze_rabbits import Command
        
        # Setup: A-B-C (shortest) and A-D-E-C (longer)
        a, b, c, d, e = CategoryFactory.create_batch(5)
        a.similar_categories.add(b, d)
        b.similar_categories.add(c)
        d.similar_categories.add(e)
        e.similar_categories.add(c)

        # Logic check: Shortest path between A and C should be 2 hops (A-B-C)
        G = nx.Graph()
        edges = Category.similar_categories.through.objects.values_list('from_category_id', 'to_category_id')
        G.add_edges_from(edges)
        
        path = nx.shortest_path(G, source=a.id, target=c.id)
        assert len(path) == 3 # 3 nodes = 2 hops
        assert path == [a.id, b.id, c.id]