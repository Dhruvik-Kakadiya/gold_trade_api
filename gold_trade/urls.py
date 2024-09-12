from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    GoldPriceView,
    BuySellGoldView,
    TransactionHistoryView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("gold-price/", GoldPriceView.as_view(), name="gold_price"),
    path("trade/", BuySellGoldView.as_view(), name="buy_sell_gold"),
    path("transactions/", TransactionHistoryView.as_view(), name="transaction_history"),
]
