from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile', null=True, blank=True)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    id_proof_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=[
            ('PASSPORT', 'Passport'),
            ('DRIVING_LICENSE', 'Driving License'),
            ('NATIONAL_ID', 'National ID'),
            ('OTHER', 'Other')
        ]
    )
    id_proof_number = models.CharField(max_length=50, blank=True, null=True)
    id_proof_file = models.FileField(
        upload_to='customers/id_proofs/',
        blank=True,
        null=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} ({self.phone})"

    class Meta:
        ordering = ['full_name']
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'