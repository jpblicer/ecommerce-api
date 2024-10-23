from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Item

class CartAPITests(APITestCase):
    def setUp(self):
        self.apple = Item.objects.create(name="Apple", price=100, quantity=10)
        self.orange = Item.objects.create(name="Orange", price=150, quantity=5)
        self.cart_url = reverse('cart-items')
        self.checkout_url = reverse('cart-checkout')
        self.items_url = reverse('items-list')

    def test_items_list(self):
        response = self.client.get(self.items_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_add_item_to_cart(self):
        response = self.client.post(self.cart_url, {
            'item': self.apple.id,
            'quantity': 3
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['item'], self.apple.id)

    def test_add_item_to_cart_exceed_stock(self):
        response = self.client.post(self.cart_url, {
            'item': self.orange.id,
            'quantity': 10
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Requested quantity exceeds available stock", response.data['error']['en'])

    def test_cart_checkout(self):
        self.client.post(self.cart_url, {
            'item': self.apple.id,
            'quantity': 2
        })
        response = self.client.post(self.checkout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Checkout successful", response.data['message']['en'])

    def test_cart_checkout_empty(self):
        response = self.client.post(self.checkout_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Cart is empty", response.data['error']['en'])
