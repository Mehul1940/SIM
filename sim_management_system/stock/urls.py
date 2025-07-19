# stock/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Master Page
    path('master/', views.master_page, name='master'), # Often serves as the dashboard or index page

    # Device Dispatch (Add Form)
    path('device_dispatch/add/', views.device_dispatch, name='device_dispatch'),
    # Device Dispatch Records (List/Search)
    path('dispatch/', views.dispatch_item, name='dispatch'), # Renamed for clarity to avoid confusion with the add view

    # Device Dispatch Actions
    path('dispatch/edit/<int:pk>/', views.dispatch_edit, name='dispatch_edit'),
    path('dispatch/delete/<int:pk>/', views.dispatch_delete, name='dispatch_delete'),

    # Device Return (Add Form)
    path('device_return/add/', views.device_return, name='device_return'),
    # Device Return Records (List/Search)
    path('return/', views.return_item, name='return'), # Renamed for clarity

    # Device Return Actions
    path('return/edit/<int:pk>/', views.return_edit, name='return_edit'),
    path('return/delete/<int:pk>/', views.return_delete, name='return_delete'),

    path('export-stock/', views.export_stock_excel, name='export_stock_excel'),
    path('stock/import/', views.import_stock_excel, name='import_stock_excel'),

]