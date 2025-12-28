import pytest
from rest_framework.test import APIClient
from categories.tests.factories import CategoryFactory
from categories.models import Category

@pytest.fixture
def client():
    return APIClient()

@pytest.mark.django_db
def test_tree_optimization(client, django_assert_num_queries):
    """
    Ensure the tree endpoint uses constant queries regardless of tree depth.
    """
    root = CategoryFactory()
    child = CategoryFactory(parent=root)
    grandchild = CategoryFactory(parent=child)

    # We expect exactly 1 query to fetch the list (plus maybe auth overhead)
    # The view should NOT query recursively.
    with django_assert_num_queries(1):
        res = client.get('/api/categories/tree/')
    
    assert res.status_code == 200
    data = res.json()
    
    # Validate Structure
    root_node = next(x for x in data if x['id'] == root.id)
    assert len(root_node['children']) == 1
    assert root_node['children'][0]['id'] == child.id
    assert root_node['children'][0]['children'][0]['id'] == grandchild.id

@pytest.mark.django_db
def test_bulk_similarity_performance(client):
    # Create 100 categories
    cats = CategoryFactory.create_batch(100)
    
    # Create valid pairs
    pairs = []
    for i in range(0, 99):
        pairs.append([cats[i].id, cats[i+1].id])
    
    payload = {"pairs": pairs}
    
    res = client.post('/api/categories/bulk_similarity/', payload, format='json')
    assert res.status_code == 200
    assert res.json()['pairs_processed'] == 99