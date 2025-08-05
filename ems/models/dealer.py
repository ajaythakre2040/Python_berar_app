import os
import uuid
from django.db import models
from django.utils import timezone


def dealer_upload_path(instance, filename):
    ext = filename.split(".")[-1]

    unique_filename = f"{uuid.uuid4().hex}.{ext}"

    return f"ems/dealer/{unique_filename}"


class Dealer(models.Model):
    branch_id = models.CharField(
        max_length=50,
    )
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    pin_code = models.CharField(max_length=10)
    address_1 = models.TextField()
    address_2 = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )
    mobile_number = models.CharField(max_length=20)
    email = models.EmailField()
    manufacturer = models.CharField(max_length=100, blank=True, null=True)
    range = models.CharField(max_length=100, blank=True, null=True)

    image = models.ImageField(upload_to=dealer_upload_path, blank=True, null=True)
    image2 = models.ImageField(upload_to=dealer_upload_path, blank=True, null=True)
    image3 = models.ImageField(upload_to=dealer_upload_path, blank=True, null=True)

    created_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(null=True, blank=True, default=0)
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.IntegerField(null=True, blank=True, default=0)

    def soft_delete(self, user_id):
        self.deleted_at = timezone.now()
        self.deleted_by = user_id
        self.save()

    def __str__(self):
        return f"{self.name} - {self.city}"

    def save(self, *args, **kwargs):
        if self.pk:
            try:
                old = Dealer.objects.get(pk=self.pk)
                for field in ["image", "image2", "image3"]:
                    old_file = getattr(old, field)
                    new_file = getattr(self, field)
                    if old_file and old_file != new_file:
                        if os.path.isfile(old_file.path):
                            os.remove(old_file.path)
            except Dealer.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        for field in ["image", "image2", "image3"]:
            file = getattr(self, field)
            if file and os.path.isfile(file.path):
                os.remove(file.path)
        super().delete(*args, **kwargs)
