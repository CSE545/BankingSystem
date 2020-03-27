import boto3
import math
import random
from user_management.models import User


def send_otp(otp, phone_number):
    client = boto3.client(
        "sns",
        aws_access_key_id="",
        aws_secret_access_key="",
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
    digits = "123456789"
    OTP = ""

    for i in range(4):
        OTP += digits[random.randrange(0, 9, 1)]

    return OTP


def get_user_phone_number(email):
    user = User.objects.get(email=email)
    return user


def save_otp_in_db(otp, user):
    user = User.objects.get(email=user.email)
    user.userlogin.last_otp = otp
    user.userlogin.save()
