from django.db import models
from departments.models import Department

# Status Choices
STATUS_CHOICES = [
    ('available', 'Available'),
    ('dispatched', 'Dispatched'),
    ('returned', 'Returned'),
    ('lost', 'Lost'),
    ('damaged', 'Damaged'),
]

class InventoryItem(models.Model):
    location = models.ForeignKey(Department, on_delete=models.CASCADE)
    city = models.CharField(max_length=100, default='Unknown')
    mobile_no = models.CharField(max_length=50, unique=True)
    imei_no = models.CharField(max_length=50, unique=True)
    serial_number = models.CharField(max_length=50, unique=True)
    person = models.CharField(max_length=100)
    sent_parcel_by = models.CharField(max_length=100)
    collected_by = models.CharField(max_length=100)
    date = models.DateField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='available')

    def __str__(self):
        return f"{self.mobile_no} - {self.location.name} - {self.city}"

class DeviceDispatch(models.Model):
    location = models.ForeignKey(Department, on_delete=models.CASCADE)
    city = models.CharField(max_length=100, default='Unknown')
    person = models.CharField(max_length=100)
    date = models.DateField()
    mobile_no = models.CharField(max_length=50)
    imei_no = models.CharField(max_length=50)
    serial_number = models.CharField(max_length=50, blank=True, null=True)
    parcel_sent_by = models.CharField(max_length=100, blank=True, null=True)
    docket_number = models.CharField(max_length=100, blank=True, null=True)
    collected_person_name = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='dispatched')

    def __str__(self):
        return f"Dispatch: {self.mobile_no} ({self.imei_no}) to {self.person} at {self.city} ({self.location.name}) on {self.date}"

class DeviceReturn(models.Model):
    location = models.ForeignKey(Department, on_delete=models.CASCADE)
    city = models.CharField(max_length=100, default='Unknown')
    person = models.CharField(max_length=100)
    date = models.DateField()
    mobile_no = models.CharField(max_length=50)
    imei_no = models.CharField(max_length=50)
    serial_number = models.CharField(max_length=50, blank=True, null=True)
    parcel_sent_by = models.CharField(max_length=100, blank=True, null=True)
    docket_number = models.CharField(max_length=100, blank=True, null=True)
    collected_person_name = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='returned')

    def __str__(self):
        return f"Return: {self.mobile_no} ({self.imei_no}) from {self.person} at {self.city} ({self.location.name}) on {self.date}"
