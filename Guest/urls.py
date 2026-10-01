from django.urls import path
from .views import AdminLoginView,UserRegistrationAPIView,UserLoginAPIView
from .views import AddProductAPIView,ProductListAPIView,AddToCartAPIView,PlaceOrderAPIView,AdminOrderListAPIView


urlpatterns = [
    path('admin-login/', AdminLoginView.as_view(), name='admin-login'),
    path("users-registration/",UserRegistrationAPIView.as_view(),name="users-registration"),
    path("user-login/",UserLoginAPIView.as_view(),name="user-login"),
    path("add-product/",AddProductAPIView.as_view(),name="add-product"),
    path("products/",ProductListAPIView.as_view(),name="product-list"),
    path("cart/add/<int:product_id>/",AddToCartAPIView.as_view(),name="add-to-cart"),
    path("order/place/",PlaceOrderAPIView.as_view(),name="place-order"),
    path("admin/orders/",AdminOrderListAPIView.as_view(),name="admin-orders"),
]