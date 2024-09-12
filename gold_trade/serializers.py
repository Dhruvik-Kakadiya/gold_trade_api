from django.contrib.auth.models import User
from rest_framework import serializers

from gold_trade.models import Transaction, UserProfile


class UserSerializer(serializers.ModelSerializer):
    """UserSerializer for create user"""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Create user
        user = User.objects.create_user(**validated_data)

        # Create UserProfile
        UserProfile.objects.create(user=user, balance=10000.0)

        return user


class TransactionSerializer(serializers.ModelSerializer):
    """TransactionSerializer for transaction history"""
    class Meta:
        model = Transaction
        fields = ['id', 'user', 'transaction_type', 'gold_amount', 'price_per_gram', 'timestamp']
        read_only_fields = ['id', 'timestamp']