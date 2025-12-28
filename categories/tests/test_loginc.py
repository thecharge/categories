import pytest
from categories.models import Category
from categories.tests.factories import CategoryFactory
from django.core.management import call_command
from io import StringIO

@pytest.mark.django_db
class TestRabbitLogic:
    def test_rabbit_hole_calculation(self):
        """
        Creates A-B-C-D chain. 
        Longest rabbit hole should be A->D (3 hops).
        """
        c1 = CategoryFactory(name="A")
        c2 = CategoryFactory(name="B")
        c3 = CategoryFactory(name="C")
        c4 = CategoryFactory(name="D")
        c5 = CategoryFactory(name="Island2_Start") # Separate island

        # Create chain A-B-C-D
        c1.similar_categories.add(c2)
        c2.similar_categories.add(c3)
        c3.similar_categories.add(c4)

        # Create Island 2
        c5.similar_categories.add(c1) # Actually let's connect it to A to test branching
        # If A-B-C-D exists, and we add E-A.
        # Path E-A-B-C-D is 4 hops. 
        
        out = StringIO()
        call_command('analyze_rabbits', stdout=out)
        result = out.getvalue()
        
        assert "Longest Rabbit Hole found!" in result
        assert "Length: 4 hops" in result # E -> A -> B -> C -> D