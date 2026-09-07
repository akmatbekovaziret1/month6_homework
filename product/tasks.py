from csv import Error

from celery import shared_task
from time import sleep
from .models import Product
from django.conf import settings
from django.core.mail import send_mail

@shared_task
def download():
    print("Запуск...")
    sleep(20)
    raise Error
    print("Успешно")
    return "OK"


# To make Celery print info about new created product
@shared_task
def process_new_product(product_id):
    product = Product.objects.get(id = product_id)
    print (
        f"New product processed: "
        f"{product.title}, price: {product.price}"
    )
    return product.id 

# Celery will print how many products exist every minute
# Registered in shop_api/celery.py
@shared_task
def print_product_count():
    count = Product.objects.count()

    print(f"Current products count: {count}")

    return count


#Celery sends message when the product is created
@shared_task
def send_product_created_email(email, product_title):
    send_mail(
        subject="Product created",
        message=(
            f'Product "{product_title}" '
            f"was created successfully!"
        ),
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=False,
    )