import boto3
import math
import random
from user_management.models import User


def send_otp(otp, phone_number):
    client = boto3.client(
        "sns",
        aws_access_key_id="AKIAYHX35C2IYZXEK27I",
        aws_secret_access_key="vDt0u1ES0ZERzKhRq0PZLl9oveDXtv12k8/O3vJu",
        region_name="eu-west-1"
    )
    msg = 'Your otp for login is {0}'.format(otp)
    phone_number = '+1' + str(phone_number)
    print('msg', msg)
    print('phone_number', phone_number)
    client.publish(
        PhoneNumber=phone_number,
        Message=msg
    )
    print('otp sent')


def generate_otp():
    digits = "0123456789"
    OTP = ""

    for i in range(4):
        OTP += digits[math.floor(random.random() * 10)]

    return OTP


def get_user_phone_number(email):
    user = User.objects.get(email=email)
    return user.phone_number
