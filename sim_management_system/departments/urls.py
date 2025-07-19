from django.urls import path
from . import views

urlpatterns = [
    path('', views.departments_list, name='departments_list'),
    path('simcards/export/', views.export_simcards_excel, name='simcard_export'),
    path('siliguri/', views.siliguri, name='siliguri'),
    path('margdarshak/', views.margdarshak, name='margdarshak'),
    path('wb/', views.wb, name='wb'),
    path('vmc/', views.vmc, name='vmc'),
    path('local_client/', views.local_client, name='local_client'),
    path('pso/', views.pso, name='pso'),
]
