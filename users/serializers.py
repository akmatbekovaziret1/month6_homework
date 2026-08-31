from rest_framework import serializers
# from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError
from users.models import ConfirmationCode, CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class OauthCodeSerializer(serializers.Serializer):
    code = serializers.CharField()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['avatar'] = user.avatar
        # по дефолту birthdatе это date object, но для json надо перевести в string
        token['birthdate'] = str(user.birthdate) if user.birthdate else None
        return token
    
class UserBaseSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class AuthValidateSerializer(UserBaseSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only = True)


class RegisterValidateSerializer(UserBaseSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only = True)
    phone_number = serializers.CharField(
        required = False,
        allow_blank = True 
    )
    birthdate = serializers.DateField(required=False, allow_null=True)
    
    
    def validate_email(self, email):
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError('User уже существует!')

        return email

    def validate_phone_number(self, phone_number):
        if not phone_number:
            return phone_number
        
        if not phone_number.isdigit():
            raise ValidationError("Phone number must contain digits only!")
        
        if not phone_number.startswith("996"):
            raise ValidationError("Phone number must start with 996!")
        
        if len(phone_number) != 12:
            raise ValidationError("The length of phone number must be 12!")
        
        return phone_number
        
class ConfirmationSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        user_id = attrs.get('user_id')
        code = attrs.get('code')

        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            raise ValidationError('User не существует!')

        try:
            confirmation_code = ConfirmationCode.objects.get(user=user)
        except ConfirmationCode.DoesNotExist:
            raise ValidationError('Код подтверждения не найден!')

        if confirmation_code.code != code:
            raise ValidationError('Неверный код подтверждения!')

        return attrs