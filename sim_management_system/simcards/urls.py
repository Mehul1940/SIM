from django.urls import path
from . import views

urlpatterns = [
    path('', views.simcard_list, name='simcard_list'),
    path('create/', views.simcard_create, name='simcard_create'),
    path('<int:pk>/', views.simcard_detail, name='simcard_detail'),
    path('update/<int:pk>/', views.simcard_update, name='simcard_update'),
    path('delete/<int:pk>/', views.simcard_delete, name='simcard_delete'),
    path('vehicle/', views.vehicle, name='vehicle'),
    
]
