from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile, User, Review, Product
from django.db.models import Avg


# Signal to create a profile when a new user is created
@receiver(post_save, sender=User)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    if created:
        # Verify if the user instance has an associated profile
        if not Profile.objects.filter(user=instance).exists():
            Profile.objects.create(user=instance)

# Signal to save the profile whenever the user instance is saved
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # If the user instance has an associated profile, save it
    if hasattr(instance, 'profile'):
        instance.profile.save()

