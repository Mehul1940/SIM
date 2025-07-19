from django.db import models
from django.contrib.auth import get_user_model
from simcards.models import SimCard
from customers.models import Customer

User = get_user_model()

class SimAssignment(models.Model):
    sim_card = models.OneToOneField(
        SimCard,
        on_delete=models.CASCADE,
        related_name='assignment',
        to_field='mobile_number',
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='sim_assignments'
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_sims'
    )
    activation_date = models.DateField()
    expiry_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    reason = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sim_card.sim_number} → {self.customer.full_name}"

    class Meta:
        ordering = ['-activation_date']
        verbose_name = 'SIM Assignment'
        verbose_name_plural = 'SIM Assignments'
        indexes = [
            models.Index(fields=['activation_date']),
            models.Index(fields=['expiry_date']),
            models.Index(fields=['is_active']),
        ]

class AssignmentHistory(models.Model):
    assignment = models.ForeignKey(
        SimAssignment,
        on_delete=models.CASCADE,
        related_name='history'
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    change_type = models.CharField(
        max_length=20,
        choices=[
            ('CREATED', 'Created'),
            ('UPDATED', 'Updated'),
            ('DEACTIVATED', 'Deactivated'),
            ('REACTIVATED', 'Reactivated')
        ]
    )
    change_details = models.JSONField()
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']
        verbose_name = 'Assignment History'
        verbose_name_plural = 'Assignment Histories'