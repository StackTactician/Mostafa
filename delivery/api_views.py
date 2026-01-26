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

            return Order.objects.filter(driver=user) | Order.objects.filter(driver=None, status='Pending')

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

class SendOTPView(generics.GenericAPIView):
    """Send OTP to email for verification"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        from django.core.mail import send_mail
        from django.utils import timezone
        from datetime import timedelta
        import random
        from .models import EmailOTP
        
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        

        otp_code = str(random.randint(100000, 999999))
        

        EmailOTP.objects.filter(email=email, is_verified=False).delete()
        

        expires_at = timezone.now() + timedelta(minutes=5)
        EmailOTP.objects.create(
            email=email,
            otp_code=otp_code,
            expires_at=expires_at
        )
        

        try:
            send_mail(
                subject='Your Mostafa Verification Code',
                message=f'''Hi there!

Your verification code is: {otp_code}

This code will expire in 5 minutes.

If you didn't request this code, please ignore this email.

Thanks,
Mostafa Team''',
                from_email='noreply@fooddelivery.com',
                recipient_list=[email],
                fail_silently=False,
            )
            
            return Response({
                'message': 'OTP sent successfully',
                'email': email
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': f'Failed to send email: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyOTPView(generics.GenericAPIView):
    """Verify OTP code"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        from django.utils import timezone
        from .models import EmailOTP
        
        email = request.data.get('email')
        otp_code = request.data.get('otp')
        
        if not email or not otp_code:
            return Response({
                'error': 'Email and OTP are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:

            otp_obj = EmailOTP.objects.filter(
                email=email,
                otp_code=otp_code,
                is_verified=False
            ).first()
            
            if not otp_obj:
                return Response({
                    'verified': False,
                    'message': 'Invalid OTP code'
                }, status=status.HTTP_400_BAD_REQUEST)
            

            if otp_obj.is_expired():
                return Response({
                    'verified': False,
                    'message': 'OTP has expired. Please request a new one.'
                }, status=status.HTTP_400_BAD_REQUEST)
            

            otp_obj.is_verified = True
            otp_obj.save()
            
            return Response({
                'verified': True,
                'message': 'Email verified successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'Verification failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

