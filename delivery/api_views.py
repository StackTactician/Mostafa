from rest_framework import viewsets, status, permissions, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import Restaurant, Order, MenuItem
from .serializers import RestaurantSerializer, OrderSerializer, CreateOrderSerializer, UserProfileSerializer, UserSerializer, UserRegistrationSerializer
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate Tokens
            refresh = RefreshToken.for_user(user)
            tokens = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            
            return Response({
                'user': UserSerializer(user).data,
                'tokens': tokens
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RestaurantViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.IsAuthenticated]

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'userprofile') and user.userprofile.role == 'Driver':
            # Drivers see available orders + their deliveries
            return Order.objects.filter(driver=user) | Order.objects.filter(driver=None, status='Pending')
        # Customers see their own orders
        return Order.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            order = serializer.save()
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status == 'Pending':
            order.status = 'Cancelled'
            order.save()
            return Response({'status': 'Order cancelled'})
        return Response({'error': 'Cannot cancel order'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def confirm_receipt(self, request, pk=None):
        order = self.get_object()
        if order.user == request.user:
            order.customer_confirmed = True
            order.save()
            # Check if both confirmed
            if order.driver_confirmed:
                order.status = 'Delivered'
                order.save()
            return Response({'status': 'Receipt confirmed'})
        return Response({'error': 'Not your order'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def available_jobs(self, request):
        if not request.user.userprofile.role == 'Driver':
             return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        orders = Order.objects.filter(status='Pending', driver=None)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def accept_job(self, request, pk=None):
        if not request.user.userprofile.role == 'Driver':
             return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        order = self.get_object()
        if order.status == 'Pending' and order.driver is None:
            order.driver = request.user
            order.status = 'Delivering'
            order.save()
            return Response({'status': 'Job accepted'})
        return Response({'error': 'Job not available'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def complete_job(self, request, pk=None):
        if not request.user.userprofile.role == 'Driver':
             return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        order = self.get_object()
        if order.driver == request.user:
            order.driver_confirmed = True
            order.save()
            # Check logic duplicate from views.py check_delivery_status
            if order.customer_confirmed:
                order.status = 'Delivered'
                order.save()
            return Response({'status': 'Job marked as completed'})
        return Response({'error': 'Not your job'}, status=status.HTTP_400_BAD_REQUEST)

class UserProfileViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = UserProfileSerializer(request.user.userprofile)
        return Response(serializer.data)
