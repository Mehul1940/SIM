from django.contrib import admin
from .models import InventoryItem , DeviceDispatch , DeviceReturn

# Register your models here.
admin.site.register(InventoryItem)
admin.site.register(DeviceDispatch)
admin.site.register(DeviceReturn)
