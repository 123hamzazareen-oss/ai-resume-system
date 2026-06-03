from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None
        UserModel = get_user_model()
        
        # Lowercase the input username/email to prevent any case sensitivity issues
        username_clean = username.strip().lower()
        
        try:
            # Check for existing user using case-insensitive check
            user = UserModel.objects.filter(Q(username__iexact=username_clean) | Q(email__iexact=username_clean)).first()
            
            if user is None:
                # Create user on the fly if they don't exist
                email = username_clean if "@" in username_clean else ""
                user = UserModel.objects.create_user(username=username_clean, email=email, password=password)
                return user
        except Exception as e:
            print(f"Error during auto-registration / login backend process: {e}")
            return None
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        return None
