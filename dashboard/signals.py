from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import User

# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def ensure_User(sender, instance, created, **kwargs):
#     if created:
#         User.objects.create(user=instance, role=User.ROLE_STAFF)
