from decimal import Decimal

from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer
import redis
import requests
from django.conf import settings
from threading import Thread, Lock
from django.db import transaction
from .models import UserProfile, Transaction
from django.core.paginator import Paginator
from .serializers import TransactionSerializer

lock = Lock()  # A lock to handle concurrency issues


# Redis Configuration
redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)


class RegisterView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        """API to Register user with username, email and password"""

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        """API to login into the system with username and password"""

        username = request.data.get('username')
        password = request.data.get('password')

        try:
            # Fetch user object if exist
            user = User.objects.get(username=username)

            # Check password
            if not user.check_password(password):
                raise ValueError('Incorrect password')

            # Create JWT tokens
            refresh = RefreshToken.for_user(user)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'error': 'Invalid username/password'}, status=status.HTTP_401_UNAUTHORIZED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)


class GoldPriceView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """API to fetch gold price"""

        gold_price = redis_instance.get('gold_price')

        # Check gold_price is stored in redis or not
        if not gold_price:
            params = {
                'api_key': settings.METAL_GOLD_PRICE_API_API_KEY,
                'base': 'USD',
                'currencies': 'XAU'
            }

            # Request to fetch gold price
            response = requests.get(settings.METAL_GOLD_PRICE_URL, params=params)
            if response.status_code == 200:
                gold_price = response.json().get('rates', {}).get('XAU')

                # Calculate gold price in USD per ounce
                gold_price = 1 / gold_price

                # Cache in Redis for 5 minutes
                redis_instance.set('gold_price', gold_price, ex=300)
            else:
                return Response({"error": "Failed to fetch gold price"}, status=response.status_code)

        return Response({'gold_price': float(gold_price)}, status=status.HTTP_200_OK)


class BuySellGoldView(APIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def post(self, request):
        user = request.user

        # 'BUY' or 'SELL'
        transaction_type = request.data.get('type')
        gold_amount = float(request.data.get('amount'))

        # Example commission rate
        commission_rate = 0.02

        # Fetch gold price from Redis
        gold_price = float(redis_instance.get('gold_price') or 0)

        if not gold_price:
            params = {
                'api_key': settings.METAL_GOLD_PRICE_API_API_KEY,
                'base': 'USD',
                'currencies': 'XAU'
            }

            # Request to fetch gold price
            response = requests.get(settings.METAL_GOLD_PRICE_URL, params=params)
            if response.status_code == 200:
                gold_price = response.json().get('rates', {}).get('XAU')

                # Calculate gold price in USD per ounce
                gold_price = 1 / gold_price

                # Cache in Redis for 5 minutes
                redis_instance.set('gold_price', gold_price, ex=300)
            else:
                return Response({"error": "Failed to fetch gold price"}, status=response.status_code)

        # Calculate total cost from gold_amount and commission_rate
        price_per_gram = gold_price * (1 + commission_rate if transaction_type == 'BUY' else 1 - commission_rate)
        total_cost = gold_amount * price_per_gram

        # Handle concurrency
        with lock:
            try:
                profile = UserProfile.objects.select_for_update().get(user=user)

                with transaction.atomic():
                    if transaction_type == 'BUY':
                        if profile.balance < Decimal(total_cost):
                            return Response({"error": "Insufficient balance."}, status=status.HTTP_400_BAD_REQUEST)
                        profile.balance -= Decimal(total_cost)
                    elif transaction_type == 'SELL':
                        profile.balance += Decimal(total_cost)

                    profile.save()

                    # Save transaction
                    Transaction.objects.create(user=user, transaction_type=transaction_type,
                                               gold_amount=gold_amount, price_per_gram=price_per_gram)

                    return Response({"message": f"Gold {transaction_type.lower()} transaction successful!"},
                                    status=status.HTTP_200_OK)

            except UserProfile.DoesNotExist:
                return Response({"error": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TransactionHistoryView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        transactions = Transaction.objects.filter(user=user).order_by('-timestamp')
        page_number = request.query_params.get('page', 1)
        paginator = Paginator(transactions, 10)  # 10 transactions per page

        try:
            page = paginator.page(page_number)
        except Exception as e:
            return Response({"error": "Invalid page number"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = TransactionSerializer(page, many=True)
        return Response({
            'total': paginator.count,
            'pages': paginator.num_pages,
            'current_page': page_number,
            'transactions': serializer.data
        }, status=status.HTTP_200_OK)