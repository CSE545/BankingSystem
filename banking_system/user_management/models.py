from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed

GENDER = (
    ("M", "MALE"),
    ("F", "FEMALE"),
    ("O", "OTHER"),
)

USER_TYPE = (
    ("T1", "TIER-1"),
    ("T2", "TIER-2"),
    ("T3", "TIER-3"),
    ("CUSTOMER", "CUSTOMER"),
    ("MERCHANT", "CORPORATE MERCHANT"),
)
# Create your models here.

# Important to implement this for Django to Recognize


class MyAccountManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, phone_number, password=None):

        if not email:
            raise ValueError('Users must have an email address')
        if not first_name:
            raise ValueError('Users must have a username')
        if not last_name:
            raise ValueError('Users must have a first name')
        if not phone_number:
            raise ValueError('Users must have a last name')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password, phone_number):

        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)
        return user

# created_at, last_login, is_admin, is_active, is_staff, is_superuser are mandatory fields.


class User(AbstractBaseUser):
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    created_at = models.DateTimeField(
        verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(
        verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    gender = models.CharField(
        max_length=6,
        choices=GENDER
    )
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name',
                       'last_name', 'password', 'phone_number']
    objects = MyAccountManager()

    def __str__(self):
        return "First name: " + self.first_name \
            + " Last name: " + self.last_name \
            + " Email: " + self.email \
            + " Phone number: " + self.phone_number \
            + " Gender: " + self.gender

    # For checking permissions. to keep it simple all admin have ALL permissons
    def has_perm(self, perm, obj=None):
        return self.is_admin

    # Does this user have permission to view this app? (ALWAYS YES FOR SIMPLICITY)
    def has_module_perms(self, app_label):
        return True


class UserLogin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    failed_attempts = models.IntegerField(default=0, blank=False)
    last_otp = models.IntegerField(blank=False, default=0)

    def __str__(self):
        return "First name: {0}".format(self.user)


@receiver(post_save, sender=User)
def user_created(sender, instance, created, **kwargs):
    if created:
        UserLogin.objects.create(user=instance)


@receiver(user_login_failed)
def login_failed(sender, credentials, request, **kwargs):
    print('login failed')
    # user = User.objects.get(email=credentials['username'])
    # user_login = UserLogin.objects.get(user=type(user))
    # print(user_login)


@receiver(user_logged_in)
def login_successful(sender, user, request, **kwargs):
    print('login successful')
