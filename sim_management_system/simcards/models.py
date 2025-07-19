from django.db import models
from departments.models import Department
from carriers.models import Carrier

class SimType(models.TextChoices):
    AIRTEL = 'Airtel', 'Airtel'
    IDEA = 'Idea', 'Idea'
    JIO = 'Jio', 'Jio'
    BSNL = 'BSNL', 'BSNL'
    Not_Assigned = 'Not_Assigned', 'Not_Assigned'

class SimStatus(models.TextChoices):
    AVAILABLE = 'Available'
    DISABLE = 'DISABLE'
    ACTIVE = 'ACTIVE'
    DEACTIVE = 'DEACTIVE'
    IDLE = 'IDLE'
    Repair = 'Repair'
    Communication_Lost = 'Communication_Lost'
    GPS_Missing = 'GPS_Missing'
    Temporary_Withdrawal ='Temporary_Withdrawal'
    Accident = 'Accident'
    Scrap = 'Scrap'
    No_Vehicle = 'No_Vehicle'


class PlanType(models.TextChoices):
    PREPAID = 'PREPAID', 'Prepaid'
    POSTPAID = 'POSTPAID', 'Postpaid'
    MONTHLY = 'MONTHLY', 'Monthly'
    OTHER = 'OTHER', 'Other'  

class SimCard(models.Model):
    mobile_number = models.CharField(
        max_length=15,
        unique=True,  
    )
    iccid_number = models.CharField(max_length=20,blank=True, null=True)  
    imsi_number = models.CharField(max_length=25, blank=True, null=True)
    basket_name = models.CharField(max_length=100, blank=True, null=True)
    sim_status = models.CharField(max_length=20, choices=SimStatus.choices, default=SimStatus.AVAILABLE)
    plan_name = models.CharField(max_length=100, blank=True, null=True)
    plan_type = models.CharField(max_length=50, blank=True, null=True)
    sim_type = models.CharField(
        max_length=20,
        choices=SimType.choices,
        default=SimType.Not_Assigned
    )
    
    imei_number = models.CharField(max_length=20, blank=True, null=True)
    current_ip = models.GenericIPAddressField(blank=True, null=True)
    last_connected = models.DateTimeField(blank=True, null=True)

    action = models.CharField(max_length=50, blank=True, null=True)
    new_sim_number = models.CharField(max_length=20, blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    remark1 = models.TextField(blank=True, null=True)
    remark2 = models.TextField(blank=True, null=True)
    remark3 = models.TextField(blank=True, null=True)
    carrier = models.ForeignKey(Carrier, on_delete=models.SET_NULL, null=True, blank=True, related_name='simcards') 
    department = models.ForeignKey(
        Department, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='simcards'
    )

    vehicle_reg_no = models.CharField(max_length=20, blank=True, null=True)
    transporter_name = models.CharField(max_length=100, blank=True, null=True)
    device_company = models.CharField(max_length=100, blank=True, null=True)
    starting_odo_meter = models.PositiveIntegerField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.iccid_number} ({self.mobile_number})"

    class Meta:
        verbose_name = "SIM Card"
        verbose_name_plural = "SIM Cards"
        ordering = ['-created_at']
