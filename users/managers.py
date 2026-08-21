from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Поле email обязательно!")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        phone_number = extra_fields.get("phone_number")
        
        
        if not phone_number.isdigit():
            raise ValueError("Phone number must contain only digits!")
        
        if not phone_number:
            raise ValueError("Superuser must have phone number!")
        
        if not phone_number.startswith("996"):
            raise ValueError("Phone number must start with 996!")
        
        if len(phone_number) != 12:
            raise ValueError("The length of phone number must be 12!")
        
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_active") is not True:
            raise ValueError("Superuser must have is_active=True!")
        
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True!")
        
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True!")
        return self.create_user(email, password, **extra_fields)
