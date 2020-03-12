from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_login_failed

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

REQUEST_STATUS = (
    ("NEW", "NEW"),
    ("APPROVED", "APPROVED"),
    ("REJECTED", "REJECTED"),
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
        return "First name: {0},  Last name: {1},  \
                Email: {2},  Phone number: {3},  Gender: {4}" \
                .format(self.first_name, self.last_name,
                        self.email, self.phone_number,
                        self.gender)

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


class UserPendingApproval(models.Model):
    created_by = models.ForeignKey(
        User, default=None, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=REQUEST_STATUS,
        default='NEW'
    )
    email = models.EmailField(verbose_name="email",
                              max_length=60, null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    gender = models.CharField(
        max_length=6,
        choices=GENDER,
        null=True,
        blank=True
    )

    def __str__(self):
        return "Created by: {0}, Status: {1}".format(self.created_by, self.status)

    def __init__(self, *args, **kwargs):
        super(UserPendingApproval, self).__init__(*args, **kwargs)
        self.old_status = self.status

    def save(self, force_insert=False, force_update=False):
        if self.old_status == 'NEW':
            print('Status changed from NEW to {0}'.format(self.status))
            if self.status == 'APPROVED':
                User.objects.filter(user_id=self.created_by.user_id).update(
                    email=self.email,
                    phone_number=self.phone_number,
                    first_name=self.first_name,
                    last_name=self.last_name,
                    gender=self.gender
                )
                self.delete()
        else:
            super(UserPendingApproval, self).save(force_insert, force_update)
            self.old_status = self.status


@receiver(post_save, sender=User)
def user_created(sender, instance, created, **kwargs):
    if created:
        UserLogin.objects.create(user=instance)


@receiver(user_login_failed)
def login_failed(sender, credentials, request, **kwargs):
    try:
        if 'username' in credentials:
            user = User.objects.get(email=credentials['username'])
            user.userlogin.failed_attempts = user.userlogin.failed_attempts + 1
            user.userlogin.save()
    except User.DoesNotExist:
        print('Login failed: User does not exist')

class EMP_Transaction(models.Model):
    Action = (
       ('create','Creating a Transaction'),
       ('Authorize','Authorizing a transaction'),
       ('view','viewing specific transaction'),
    )

    action=models.CharField(max_length=32,choices=Action,default='view')
    cust_name= models.TextField(max_length=32,default=None)
    to= models.TextField(max_length=32,default=None)
    transaction_ammount=models.DecimalField(decimal_places=2 ,max_digits=10,default=None)


