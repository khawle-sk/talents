
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import (
    Skill, Language, Project, TalentProfile,
    TalentProfileSkill, TalentProfileLanguage,
    TalentProfileFeaturedProject, TalentValidation
)
from .serializers import (
    SkillSerializer, LanguageSerializer, ProjectSerializer,
    TalentProfileSerializer, TalentValidationSerializer,
    TalentProfileDetailSerializer
)

class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'category']
    filterset_fields = ['category']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

class LanguageViewSet(viewsets.ModelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TalentProfileViewSet(viewsets.ModelViewSet):
    serializer_class = TalentProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return TalentProfile.objects.all()
        return TalentProfile.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TalentProfileDetailSerializer
        return TalentProfileSerializer
    
    @action(detail=False, methods=['GET', 'POST', 'PUT', 'PATCH'])
    def my_profile(self, request):
        profile, created = TalentProfile.objects.get_or_create(user=request.user)
        
        if request.method == 'GET':
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        
        elif request.method in ['POST', 'PUT', 'PATCH']:
            serializer = self.get_serializer(
                profile,
                data=request.data,
                partial=request.method == 'PATCH'
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
    
    @action(detail=True, methods=['POST'])
    def add_skill(self, request, pk=None):
        profile = self.get_object()
        skill_id = request.data.get('skill_id')
        
        if not skill_id:
            return Response(
                {'error': 'skill_id est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        skill = get_object_or_404(Skill, id=skill_id)
        TalentProfileSkill.objects.get_or_create(
            talentprofile=profile,
            skill=skill
        )
        return Response({'message': 'Compétence ajoutée avec succès'})
    
    @action(detail=True, methods=['POST'])
    def add_language(self, request, pk=None):
        profile = self.get_object()
        language_id = request.data.get('language_id')
        
        if not language_id:
            return Response(
                {'error': 'language_id est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        language = get_object_or_404(Language, id=language_id)
        TalentProfileLanguage.objects.get_or_create(
            talentprofile=profile,
            language=language
        )
        return Response({'message': 'Langue ajoutée avec succès'})

class TalentValidationViewSet(viewsets.ModelViewSet):
    queryset = TalentValidation.objects.all()
    serializer_class = TalentValidationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return TalentValidation.objects.all()
        return TalentValidation.objects.filter(user=self.request.user)