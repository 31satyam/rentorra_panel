from django.urls import path
from . import views

urlpatterns = [
    path('', views.property_list_view, name='property_list'),
    path('location/<slug:slug>/', views.location_landing_view, name='properties_by_location'),
    path('<slug:slug>/', views.property_detail_view, name='property_detail'),
]
