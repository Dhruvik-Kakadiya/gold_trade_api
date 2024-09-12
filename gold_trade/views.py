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
