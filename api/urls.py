from django.urls import path
from .views import NationalIDView

urlpatterns = [
    path('national-id/', NationalIDView.as_view(), name='national_id'),
]
