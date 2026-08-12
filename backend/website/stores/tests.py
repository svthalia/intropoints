from django.db import IntegrityError
from django.test import TestCase

from stores.models.items import Item
from stores.models.stores import Store
from tournaments.models import Tournament


def make_store(name="store", slug="t"):
    tournament = Tournament.objects.create(name=slug, slug=slug)
    return Store.objects.create(tournament=tournament, name=name)


class StoreModelTests(TestCase):
    """Tests the Store model."""

    def test_string_representation(self):
        store = make_store(name="Market")
        self.assertEqual(str(store), f"Store: Market for Tournament: {store.tournament.name}")

    def test_one_to_one_with_tournament(self):
        store = make_store()
        self.assertEqual(store.tournament.store, store)


class ItemModelTests(TestCase):
    """Tests the Item model."""

    def test_creation_fields(self):
        store = make_store()
        item = Item.objects.create(store=store, name="Potion", description="d", price=50)

        self.assertEqual(item.name, "Potion")
        self.assertEqual(item.price, 50)

    def test_string_representation(self):
        store = make_store()
        item = Item.objects.create(store=store, name="Shield", description="d", price=10)
        self.assertEqual(str(item), "Shield")

    def test_unique_together_store_name(self):
        store = make_store()
        Item.objects.create(store=store, name="Sword", description="d", price=10)
        with self.assertRaises(IntegrityError):
            Item.objects.create(store=store, name="Sword", description="d", price=20)

    def test_price_filtering(self):
        store = make_store()
        cheap = Item.objects.create(store=store, name="Cheap", description="d", price=5)
        pricey = Item.objects.create(store=store, name="Pricey", description="d", price=500)

        results = Item.objects.filter(price__gte=100)
        self.assertIn(pricey, results)
        self.assertNotIn(cheap, results)
