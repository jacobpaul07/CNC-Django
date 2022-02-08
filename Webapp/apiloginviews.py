# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import status, permissions
from .serializers import CustomTokenRefreshSerializer, MyTokenObtainPairSerializer, CustomUserSerializer
from rest_framework_simplejwt.tokens import RefreshToken


class ObtainTokenPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    

class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer


class CustomUserCreate(APIView):
    permission_classes = (permissions.IsAdminUser,)
    authentication_classes = ()

    @staticmethod
    def post(request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                json = serializer.data
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAndBlacklistRefreshTokenForUserView(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    @staticmethod
    def post(request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as ex:
            print("Error", ex)
            return Response(status=status.HTTP_400_BAD_REQUEST)
