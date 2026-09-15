from django.urls import path
from . import views

urlpatterns = [
    path('click/<int:ad_id>/', views.ad_click_redirect_view, name='ad_click'),
]
