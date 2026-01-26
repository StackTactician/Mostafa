from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from delivery.models import UserProfile, Order, Restaurant, MenuItem, OrderItem

class OrderTests(APITestCase):
    def setUp(self):
        # Create Users
        self.customer = User.objects.create_user(username='customer', password='password123')
        UserProfile.objects.create(user=self.customer, role='Customer')
        
        self.driver = User.objects.create_user(username='driver', password='password123')
        UserProfile.objects.create(user=self.driver, role='Driver')
        
        # Create Restaurant & Menu
        self.restaurant = Restaurant.objects.create(
            name="Test Resto", 
            description="Test Desc",
            address="123 Test St"
        )
        self.menu_item = MenuItem.objects.create(
            restaurant=self.restaurant,
            name="Test Item",
            description="Yum",
            price=10.00
        )
        
        # Auth Headers
        self.customer_client = self.client_class()
        self.customer_client.force_authenticate(user=self.customer)
        
        self.driver_client = self.client_class()
        self.driver_client.force_authenticate(user=self.driver)

    def test_create_order(self):
        """Test creating an order"""
        url = reverse('order-list')
        data = {'items': {str(self.menu_item.id): 2}}
        
        response = self.customer_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Order.objects.first().total_price, 20.00)

    def test_driver_accept_job(self):
        """Test driver accepting a job"""
        # Create pending order
        order = Order.objects.create(user=self.customer, total_price=10.00)
        OrderItem.objects.create(order=order, menu_item=self.menu_item, price_at_time=10.00)
        
        url = reverse('order-accept-job', args=[order.id])
        response = self.driver_client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.driver, self.driver)
        self.assertEqual(order.status, 'Delivering')

    def test_dual_confirmation(self):
        """Test dual confirmation flow"""
        order = Order.objects.create(
            user=self.customer, 
            driver=self.driver, 
            status='Delivering',
            total_price=10.00
        )
        
        # Driver confirms
        url_drive = reverse('order-complete-job', args=[order.id])
        resp1 = self.driver_client.post(url_drive)
        self.assertEqual(resp1.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertTrue(order.driver_confirmed)
        self.assertEqual(order.status, 'Delivering') # Not yet delivered
        
        # Customer confirms
        url_cust = reverse('order-confirm-receipt', args=[order.id])
        resp2 = self.customer_client.post(url_cust)
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertTrue(order.customer_confirmed)
        self.assertEqual(order.status, 'Delivered') # Now delivered
