from django.db import models
from django.core.validators import MinLengthValidator

class Carrier(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(
        max_length=10,
        unique=True,
        validators=[MinLengthValidator(2)]
    )
    support_email = models.EmailField(blank=True, null=True)
    support_phone = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        ordering = ['name']
        verbose_name = 'Carrier'
        verbose_name_plural = 'Carriers'