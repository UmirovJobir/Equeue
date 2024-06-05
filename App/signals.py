import os
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import BusinessImage, Employee


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