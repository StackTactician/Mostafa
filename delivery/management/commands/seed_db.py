import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from delivery.models import UserProfile, Restaurant, MenuItem, Order, OrderItem
from faker import Faker
from django.utils import timezone

fake = Faker()

class Command(BaseCommand):
    help = 'Seeds the database with mock data'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=10, help='Number of users to create')
        parser.add_argument('--restaurants', type=int, default=5, help='Number of restaurants to create')
        parser.add_argument('--orders', type=int, default=20, help='Number of orders to create')

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')
        
        users_count = options['users']
        restaurants_count = options['restaurants']
        orders_count = options['orders']

        # Create Users
        customers = []
        drivers = []
        
        for _ in range(users_count):
            username = fake.user_name()
            # Ensure unique username
            while User.objects.filter(username=username).exists():
                username = fake.user_name() + str(random.randint(1, 1000))
                
            user = User.objects.create_user(
                username=username,
                email=fake.email(),
                password='pass1234'
            )
            
            role = random.choice(['Customer', 'Driver'])
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.role = role
            profile.phone_number = fake.phone_number()[:15] # Limit length
            
            if role == 'Customer':
                profile.address = fake.address()
                customers.append(user)
            else:
                profile.vehicle_type = random.choice(['Bike', 'Car', 'Scooter'])
                profile.vehicle_plate = fake.license_plate()
                profile.license_number = fake.bothify(text='??-#####')
                profile.is_available = random.choice([True, False])
                drivers.append(user)
            
            profile.save()
            
        self.stdout.write(self.style.SUCCESS(f'Created {users_count} users'))

        # Create Restaurants
        restaurants = []
        for _ in range(restaurants_count):
            restaurant = Restaurant.objects.create(
                name=fake.company() + " Food",
                address=fake.address(),
                description=fake.catch_phrase()
            )
            restaurants.append(restaurant)
            
            # Create Menu Items
            for _ in range(random.randint(5, 10)):
                MenuItem.objects.create(
                    restaurant=restaurant,
                    name=fake.word().title() + " " + random.choice(['Burger', 'Pizza', 'Salad', 'Soup', 'Pasta']),
                    description=fake.sentence(),
                    price=round(random.uniform(5.0, 30.0), 2)
                )
        
        self.stdout.write(self.style.SUCCESS(f'Created {restaurants_count} restaurants'))

        # Create Orders
        if not customers or not restaurants:
            self.stdout.write(self.style.WARNING('Not enough customers or restaurants to create orders'))
            return

        for _ in range(orders_count):
            customer = random.choice(customers)
            restaurant = random.choice(restaurants)
            menu_items = list(restaurant.menu_items.all())
            
            if not menu_items:
                continue
                
            status = random.choice(['Pending', 'In Progress', 'Delivering', 'Delivered'])
            driver = None
            if status in ['Delivering', 'Delivered'] and drivers:
                driver = random.choice(drivers)
            
            order = Order.objects.create(
                user=customer,
                status=status,
                total_price=0, # Will update
                driver=driver,
                created_at=fake.date_time_between(start_date='-30d', end_date='now', tzinfo=timezone.get_current_timezone())
            )
            
            # Add items
            total = 0
            for _ in range(random.randint(1, 4)):
                item = random.choice(menu_items)
                OrderItem.objects.create(
                    order=order,
                    menu_item=item,
                    quantity=random.randint(1, 2),
                    price_at_time=item.price
                )
                total += item.price
            
            order.total_price = total
            order.save()

        self.stdout.write(self.style.SUCCESS(f'Created {orders_count} orders'))
