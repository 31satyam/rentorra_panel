from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.property_enquiry_create_view, name='property_enquiry_submit'),
    path('success/', views.enquiry_success_view, name='enquiry_success'),
]
