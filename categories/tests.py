import pytest
from rest_framework.test import APIClient
from .models import Category

@pytest.fixture
def client():
    return APIClient()

@pytest.mark.django_db
def test_full_flow(client):
    # 1. Create Data
    a = Category.objects.create(name="A")
    b = Category.objects.create(name="B", parent=a)
    c = Category.objects.create(name="C")
    
    # 2. Test Tree
    res = client.get("/api/categories/tree/")
    assert res.status_code == 200
    tree = res.json()
    
    # "A" should be a root, "B" should be its child
    root_a = next(node for node in tree if node['id'] == a.id)
    assert root_a['children'][0]['id'] == b.id

    # 3. Test Similarity Bulk
    payload = {"pairs": [[a.id, c.id]]}
    res = client.post("/api/categories/bulk_similarity/", payload, format='json')
    assert res.status_code == 200
    
    # Verify A is similar to C
    assert a.similar_categories.filter(id=c.id).exists()