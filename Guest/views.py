from django.contrib.auth import authenticate

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework.permissions import (
    BasePermission,
    IsAuthenticated
)

from rest_framework_simplejwt.tokens import RefreshToken

from .models import (
    UserRegistration,
    Product,
    ProductImage,Cart, CartItem,Order,OrderItem
)

from .serializers import (
    AdminLoginSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
    ProductSerializer,
    CartItemSerializer
)


# =====================================================
# LOGIN PERMISSION
# =====================================================

class IsLoginAllowed(BasePermission):

    message = "Only POST request is allowed."

    def has_permission(self, request, view):
        return request.method == "POST"


# =====================================================
# ADMIN PERMISSION
# =====================================================

class IsAdmin(BasePermission):

    message = "Only authenticated admin users are allowed."

    def has_permission(self, request, view):

        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_superuser
        )


# =====================================================
# ADMIN LOGIN
# =====================================================

class AdminLoginView(APIView):

    permission_classes = [IsLoginAllowed]

    def post(self, request):

        serializer = AdminLoginSerializer(
            data=request.data
        )

        if not serializer.is_valid():

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        user = authenticate(
            username=username,
            password=password
        )

        if user is None:

            return Response(
                {
                    "error": "Invalid admin username or password"
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_superuser:

            return Response(
                {
                    "error": "Only admin users are allowed"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Admin login successful",
                "user_id": user.id,
                "username": user.username,
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            },
            status=status.HTTP_200_OK
        )


# =====================================================
# USER REGISTRATION
# =====================================================

class UserRegistrationAPIView(APIView):

    def get(self, request):

        users = UserRegistration.objects.all()

        serializer = UserRegistrationSerializer(
            users,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request):

        serializer = UserRegistrationSerializer(
            data=request.data
        )

        if serializer.is_valid():

            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


# =====================================================
# USER LOGIN
# =====================================================

class UserLoginAPIView(APIView):

    def post(self, request):

        serializer = UserLoginSerializer(
            data=request.data
        )

        if serializer.is_valid():

            user = serializer.validated_data["user"]

            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "message": "Login successful",
                    "user_id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "refresh": str(refresh),
                    "access": str(refresh.access_token)
                },
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


# =====================================================
# ADD PRODUCT
# =====================================================

class AddProductAPIView(APIView):

    # Only admin can add products
    permission_classes = [IsAdmin]

    def post(self, request):

        serializer = ProductSerializer(
            data=request.data
        )

        if not serializer.is_valid():

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create product
        product = serializer.save()

        # Get multiple uploaded images
        images = request.FILES.getlist("images")

        # Save images to Cloudinary
        for image in images:

            ProductImage.objects.create(
                product=product,
                image=image
            )

        # Serialize created product
        product_serializer = ProductSerializer(
            product
        )

        return Response(
            {
                "message": "Product added successfully",
                "product": product_serializer.data
            },
            status=status.HTTP_201_CREATED
        )


# =====================================================
# PRODUCT LIST
# =====================================================

class ProductListAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        products = Product.objects.all().order_by("-id")

        serializer = ProductSerializer(
            products,
            many=True
        )

        return Response(
            {
                "message": "Products fetched successfully",
                "products": serializer.data
            },
            status=status.HTTP_200_OK
        )

class AddToCartAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {
                    "message": "Product not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            user = UserRegistration.objects.get(
                id=request.user.id
            )
        except UserRegistration.DoesNotExist:
            return Response(
                {
                    "message": "User not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        cart, created = Cart.objects.get_or_create(
            user=user
        )

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product
        )

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        return Response(
            {
                "message": "Product added to cart successfully",
                "product": product.name,
                "quantity": cart_item.quantity
            },
            status=status.HTTP_200_OK
        )


class PlaceOrderAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        # Get logged-in user
        try:
            user = UserRegistration.objects.get(
                id=request.user.id
            )
        except UserRegistration.DoesNotExist:
            return Response(
                {
                    "message": "User not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # Get user's cart
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response(
                {
                    "message": "Cart is empty"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_items = CartItem.objects.filter(cart=cart)

        if not cart_items.exists():
            return Response(
                {
                    "message": "Cart is empty"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Calculate total
        total_amount = 0

        for item in cart_items:

            item_total = item.product.price * item.quantity

            total_amount += item_total

        # Create order
        order = Order.objects.create(
            user=user,
            total_amount=total_amount
        )

        # Create order items
        for item in cart_items:

            item_total = item.product.price * item.quantity

            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
                total_price=item_total
            )

        # Clear cart
        cart_items.delete()

        return Response(
            {
                "message": "Order placed successfully",
                "order_id": order.id,
                "total_amount": order.total_amount,
                "status": order.status
            },
            status=status.HTTP_201_CREATED
        )


class AdminOrderListAPIView(APIView):

    permission_classes = [IsAdmin]

    def get(self, request):

        orders = Order.objects.all().order_by("-id")

        order_data = []

        for order in orders:

            items = OrderItem.objects.filter(order=order)

            item_data = []

            for item in items:

                item_data.append({
                    "product_id": item.product.id,
                    "product_name": item.product.name,
                    "quantity": item.quantity,
                    "price": item.price,
                    "total_price": item.total_price
                })

            order_data.append({
                "order_id": order.id,
                "user_id": order.user.id,
                "user_name": order.user.name,
                "user_email": order.user.email,
                "total_amount": order.total_amount,
                "status": order.status,
                "created_at": order.created_at,
                "items": item_data
            })

        return Response(
            {
                "message": "Orders fetched successfully",
                "orders": order_data
            },
            status=status.HTTP_200_OK
        )