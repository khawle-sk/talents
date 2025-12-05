

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'skills', views.SkillViewSet, basename='skill')
router.register(r'languages', views.LanguageViewSet, basename='language')
router.register(r'projects', views.ProjectViewSet, basename='project')
router.register(r'talent-profiles', views.TalentProfileViewSet, basename='talentprofile')
router.register(r'validations', views.TalentValidationViewSet, basename='validation')

urlpatterns = [
    path('', include(router.urls)),
    path('talent-profiles/my_profile/', views.TalentProfileViewSet.as_view(
        {'get': 'my_profile', 'post': 'my_profile', 'put': 'my_profile', 'patch': 'my_profile'}
    )),
]
