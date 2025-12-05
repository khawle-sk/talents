from django.urls import path
from . import views

urlpatterns = [
    path('talent-cloud/', views.TalentCloudView.as_view(), name='talent-cloud'),
    path('talent-map/', views.TalentMapView.as_view(), name='talent-map'),
    path('stats/', views.StatsView.as_view(), name='stats'),
]