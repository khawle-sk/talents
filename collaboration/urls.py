from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'requests', views.CollaborationRequestViewSet, basename='collaborationrequest')
router.register(r'applications', views.CollaborationApplicationViewSet, basename='collaborationapplication')

urlpatterns = [
    path('', include(router.urls)),
]