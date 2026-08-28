from datetime import date 
from rest_framework.exceptions import ValidationError

def validate_product_creation_age(birthdate):
    if not birthdate:
        raise ValidationError(
            "Укажите дату рождения, чтобы создать продукт."
        )
    
    birthdate = date.fromisoformat(birthdate)
    
    today = date.today()
    
    age = today.year - birthdate.year 
    # дополнительно чекаем
    if (today.month, today.day) - (birthdate.month, birthdate.day):
        age -= 1
        
    if age<18:
        raise ValidationError(
            "Вам должно быть 18 лет, чтобы создать продукт."
        )
    