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
                return None
        except Exception as e:
            print(f"Error during login backend process: {e}")
            return None
        
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

