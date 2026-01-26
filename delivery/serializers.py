from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Restaurant, MenuItem, Order, OrderItem, UserProfile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = UserProfile
        fields = ['user', 'role', 'phone_number', 'address', 'license_number', 'vehicle_plate', 'is_available']

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'description', 'price', 'image']

class RestaurantSerializer(serializers.ModelSerializer):
    menu_items = MenuItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'description', 'cuisine', 'address', 'menu_items']

class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)
    price = serializers.DecimalField(source='price_at_time', max_digits=6, decimal_places=2, read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item_name', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    restaurant_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ['id', 'status', 'total_price', 'created_at', 'items', 'restaurant_name']
        
    def get_restaurant_name(self, obj):
        if obj.items.exists():
            return obj.items.first().menu_item.restaurant.name
        return "Unknown"

class UserRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=[('Customer', 'Customer'), ('Driver', 'Driver')])
    phone_number = serializers.CharField(required=False, allow_blank=True)
    

    address = serializers.CharField(required=False, allow_blank=True)
    

    license_number = serializers.CharField(required=False, allow_blank=True)
    vehicle_plate = serializers.CharField(required=False, allow_blank=True)
    vehicle_type = serializers.CharField(required=False, allow_blank=True)
    bank_account = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        user_data = {k: validated_data.get(k) for k in ['username', 'email', 'password']}
        user = User.objects.create_user(**user_data)
        

        profile_data = {
            'role': validated_data.get('role'),
            'phone_number': validated_data.get('phone_number'),
            'address': validated_data.get('address'),
            'license_number': validated_data.get('license_number'),
            'vehicle_plate': validated_data.get('vehicle_plate'),
            'vehicle_type': validated_data.get('vehicle_type'),
            'bank_account': validated_data.get('bank_account'),
        }
        

        profile = user.userprofile
        for attr, value in profile_data.items():
            if value:
                setattr(profile, attr, value)
        profile.save()
        return user

class CreateOrderSerializer(serializers.Serializer):

    items = serializers.DictField(child=serializers.IntegerField())

    def create(self, validated_data):
        user = self.context['request'].user
        items_data = validated_data['items']
        

        total_price = 0
        order = Order.objects.create(user=user, total_price=0)
        
        for item_id, quantity in items_data.items():
            try:
                menu_item = MenuItem.objects.get(id=item_id)
                OrderItem.objects.create(
                    order=order,
                    menu_item=menu_item,
                    quantity=quantity,
                    price_at_time=menu_item.price
                )
                total_price += menu_item.price * quantity
            except MenuItem.DoesNotExist:
                pass
        
        order.total_price = total_price
        order.save()
        return order
