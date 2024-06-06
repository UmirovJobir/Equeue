import os
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models import *


@receiver(post_delete, sender=BusinessImage)
def delete_business_image(sender, instance, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)


@receiver(post_delete, sender=Employee)
def delete_employee_image(sender, instance, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)

@receiver(pre_save, sender=Employee)
def delete_old_employee_image(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_instance = Employee.objects.get(pk=instance.pk)
    except Employee.DoesNotExist:
        return False

    old_image = old_instance.image
    if old_image and old_image != instance.image:
        if os.path.isfile(old_image.path):
            os.remove(old_image.path)


@receiver(pre_save, sender=Business)
def delete_old_logo_on_update(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_instance = Business.objects.get(pk=instance.pk)
    except Business.DoesNotExist:
        return False

    old_logo = old_instance.logo
    new_logo = instance.logo

    if old_logo and old_logo != new_logo:
        if os.path.isfile(old_logo.path):
            os.remove(old_logo.path)