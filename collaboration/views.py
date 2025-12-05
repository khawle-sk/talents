from django.shortcuts import render

# # Create your views here.

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import CollaborationRequest, CollaborationApplication
from .serializers import (
    CollaborationRequestSerializer, 
    CollaborationApplicationSerializer,
    CollaborationRequestCreateSerializer
)

class CollaborationRequestViewSet(viewsets.ModelViewSet):
    queryset = CollaborationRequest.objects.all()
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['title', 'description']
    filterset_fields = ['is_active']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CollaborationRequestCreateSerializer
        return CollaborationRequestSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            # Voir ses propres demandes + demandes actives
            return CollaborationRequest.objects.filter(
                Q(creator=user) | Q(is_active=True)
            ).distinct()
        # Non authentifié : seulement les demandes actives
        return CollaborationRequest.objects.filter(is_active=True)
    
    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)
    
    @action(detail=True, methods=['POST'])
    def apply(self, request, pk=None):
        collaboration = self.get_object()
        
        if not collaboration.is_active:
            return Response(
                {'error': 'Cette collaboration n\'est plus active'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier si l'utilisateur a déjà postulé
        existing = CollaborationApplication.objects.filter(
            request=collaboration,
            applicant=request.user
        ).first()
        
        if existing:
            return Response(
                {'error': 'Vous avez déjà postulé à cette collaboration'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        application = CollaborationApplication.objects.create(
            request=collaboration,
            applicant=request.user,
            message=request.data.get('message', '')
        )
        
        serializer = CollaborationApplicationSerializer(application)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['GET'])
    def applications(self, request, pk=None):
        collaboration = self.get_object()
        
        # Vérifier que l'utilisateur est le créateur
        if collaboration.creator != request.user:
            return Response(
                {'error': 'Vous n\'êtes pas autorisé à voir les candidatures'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        applications = collaboration.collaborationapplication_set.all()
        serializer = CollaborationApplicationSerializer(applications, many=True)
        return Response(serializer.data)

class CollaborationApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = CollaborationApplicationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        # Voir ses propres candidatures + candidatures pour ses demandes
        return CollaborationApplication.objects.filter(
            Q(applicant=user) | Q(request__creator=user)
        ).distinct()
    
    @action(detail=True, methods=['POST'])
    def accept(self, request, pk=None):
        application = self.get_object()
        
        # Vérifier que l'utilisateur est le créateur de la collaboration
        if application.request.creator != request.user:
            return Response(
                {'error': 'Vous n\'êtes pas autorisé à accepter cette candidature'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        application.accepted = True
        application.save()
        
        # Désactiver la collaboration
        application.request.is_active = False
        application.request.save()
        
        serializer = self.get_serializer(application)
        return Response(serializer.data)