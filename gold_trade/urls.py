from django.urls import path
from .views import RegisterView, LoginView, GoldPriceView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('gold-price/', GoldPriceView.as_view(), name='gold_price'),
]
