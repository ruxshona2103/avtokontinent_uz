# accounts/tokens.py
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
import logging  # Agar logger dan foydalansangiz, uni ham import qilish kerak

logger = logging.getLogger(__name__)  # Agar bu qator bo'lsa, import logging bo'lishi kerak

User = get_user_model()


class CustomAccessToken(AccessToken):
    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)

        if hasattr(user, 'phone_number') and user.phone_number:
            token['phone'] = user.phone_number
        elif hasattr(user, 'phone') and user.phone:
            token['phone'] = user.phone
        else:
            logger.warning(
                f"User {user.id} ({user.username}) does not have a 'phone_number' or 'phone' field populated for JWT.")

        return token
