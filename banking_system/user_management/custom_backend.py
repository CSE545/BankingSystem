from django.contrib.auth.backends import ModelBackend
from user_management.models import User


class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None):
        try:
            user = User.objects.get(email=email)
            success = user.check_password(password)
            return user
            if success:
                return user
            else:
                return None
        except User.DoesNotExist:
            return None
        return None

    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
            if user.is_active:
                return user
            return None
        except User.DoesNotExist:
            return None
