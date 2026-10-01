from rest_framework import serializers

from .models import (
    UserRegistration,
    Product,
    ProductImage,Cart, CartItem
)


# =====================================================
# ADMIN LOGIN
# =====================================================

class AdminLoginSerializer(serializers.Serializer):

    username = serializers.CharField()

    password = serializers.CharField(
        write_only=True
    )


# =====================================================
# USER REGISTRATION
# =====================================================

class UserRegistrationSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = UserRegistration

        fields = [
            "id",
            "name",
            "email",
            "password",
            "created_at"
        ]

        extra_kwargs = {
            "password": {
                "write_only": True
            }
        }


# =====================================================
# USER LOGIN
# =====================================================

class UserLoginSerializer(serializers.Serializer):

    email = serializers.EmailField()

    password = serializers.CharField(
        write_only=True
    )

    def validate(self, data):

        email = data.get("email")
        password = data.get("password")

        try:

            user = UserRegistration.objects.get(
                email=email
            )

        except UserRegistration.DoesNotExist:

            raise serializers.ValidationError(
                "Invalid email or password"
            )

        if user.password != password:

            raise serializers.ValidationError(
                "Invalid email or password"
            )

        data["user"] = user

        return data


# =====================================================
# PRODUCT IMAGE SERIALIZER
# =====================================================

class ProductImageSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = ProductImage

        fields = [
            "id",
            "image",
            "created_at"
        ]


# =====================================================
# PRODUCT SERIALIZER
# =====================================================

class ProductSerializer(
    serializers.ModelSerializer
):

    images = ProductImageSerializer(
        many=True,
        read_only=True
    )

    class Meta:

        model = Product

        fields = [
            "id",
            "name",
            "description",
            "price",
            "stock",
            "created_at",
            "images"
        ]



class CartItemSerializer(serializers.ModelSerializer):

    product = ProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "quantity",
            "added_at"
        ]