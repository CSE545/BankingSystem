import boto3
from django_otp.oath import hotp
secret_key = b'1234567890123467890'


def sendOtp(otp, phone_number):
    client = boto3.client(
        "sns",
        aws_access_key_id="",
        aws_secret_access_key="",
        region_name="eu-west-1"
    )
    msg = 'Your otp for login is {0}'.format(otp)
    phone_number = str(phone_number)
    client.publish(
        PhoneNumber=phone_number,
        Message=msg
    )


def generateOtp():
    otp = hotp(key=secret_key, digits=6)
    return otp
