import os

import requests

from django.utils import timezone

from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken

from users.models import CustomUser
from users.serializers import OauthCodeSerializer


class GoogleLoginAPIView(CreateAPIView):
    serializer_class = OauthCodeSerializer
    
    #переписал post с помощью ИИ
    
    def post(self, request):
        code = self.get_code(request)

        access_token = self.get_google_access_token(code)
        if not access_token:
            return Response(
                {"error": "Could not get Google access token"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_info = self.get_google_user_info(access_token)

        email = user_info.get("email")
        if not email:
            return Response(
                {"error": "Google did not return an email"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = self.get_or_create_user(user_info)
        self.update_user_login_data(user, user_info)

        tokens = self.generate_tokens(user)

        return Response(
            tokens,
            status=status.HTTP_200_OK
        )

    def get_code(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return serializer.validated_data["code"]

    def get_google_access_token(self, code):
        response = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
                "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET"),
                "redirect_uri": os.environ.get("GOOGLE_REDIRECT_URI"),
                "grant_type": "authorization_code",
            }
        )

        return response.json().get("access_token")

    def get_google_user_info(self, access_token):
        response = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )

        return response.json()

    def get_or_create_user(self, user_info):
        email = user_info["email"]

        user, created = CustomUser.objects.get_or_create(
            email=email,
            defaults={
                "first_name": user_info.get("given_name", ""),
                "last_name": user_info.get("family_name", ""),
                "avatar": user_info.get("picture", ""),
                "registration_source": "google",
                "is_active": True,
            }
        )

        return user

    def update_user_login_data(self, user, user_info):
        user.first_name = user_info.get("given_name", "")
        user.last_name = user_info.get("family_name", "")
        user.avatar = user_info.get("picture", "")

        user.is_active = True
        user.last_login = timezone.now()

        user.save()

    def generate_tokens(self, user):
        refresh = RefreshToken.for_user(user)

        return {
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        }