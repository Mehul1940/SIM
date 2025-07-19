from django.urls import path
from . import views

urlpatterns = [
    path('', views.carrier_list, name='carrier_list'),
    path('create/', views.carrier_create, name='carrier_create'),
    path('<int:pk>/', views.carrier_detail, name='carrier_detail'),
    path('<int:pk>/update/', views.carrier_update, name='carrier_update'),
    path('<int:pk>/delete/', views.carrier_delete, name='carrier_delete'),
]
