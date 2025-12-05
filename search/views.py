from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.db.models import Q, Count
from users.models import User, Profile
from talents.models import Skill, TalentProfile, Project
from collaboration.models import CollaborationRequest

class SearchView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        query = request.GET.get('q', '').strip()
        search_type = request.GET.get('type', 'all')
        
        results = {}
        
        # Recherche de talents
        if search_type in ['all', 'talents']:
            talent_profiles = TalentProfile.objects.filter(
                Q(user__username__icontains=query) |
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(user__email__icontains=query)
            ).select_related('user').prefetch_related(
                'talentprofileskill_set__skill',
                'talentprofilelanguage_set__language'
            )[:20]
            
            talent_results = []
            for tp in talent_profiles:
                profile = Profile.objects.filter(user=tp.user).first()
                talent_results.append({
                    'id': tp.user.id,
                    'username': tp.user.username,
                    'full_name': tp.user.get_full_name(),
                    'email': tp.user.email,
                    'is_verified_talent': tp.user.is_verified_talent,
                    'country': profile.country if profile else None,
                    'school': profile.school if profile else None,
                    'skills': [{'id': tps.skill.id, 'name': tps.skill.name} 
                              for tps in tp.talentprofileskill_set.all()[:5]],
                    'languages': [{'id': tpl.language.id, 'name': tpl.language.name} 
                                 for tpl in tp.talentprofilelanguage_set.all()[:3]]
                })
            
            results['talents'] = talent_results
        
        # Recherche de compétences
        if search_type in ['all', 'skills']:
            skills = Skill.objects.filter(
                Q(name__icontains=query) |
                Q(category__icontains=query)
            ).annotate(
                talent_count=Count('talentprofileskill')
            ).order_by('-talent_count')[:20]
            
            results['skills'] = [
                {
                    'id': skill.id,
                    'name': skill.name,
                    'category': skill.category,
                    'talent_count': skill.talent_count
                }
                for skill in skills
            ]
        
        # Recherche de projets
        if search_type in ['all', 'projects']:
            projects = Project.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            ).select_related('user')[:20]
            
            results['projects'] = [
                {
                    'id': project.id,
                    'title': project.title,
                    'description': project.description[:200] + '...' if project.description and len(project.description) > 200 else project.description,
                    'link': project.link,
                    'user': {
                        'id': project.user.id,
                        'username': project.user.username
                    }
                }
                for project in projects
            ]
        
        # Recherche de collaborations
        if search_type in ['all', 'collaborations']:
            collaborations = CollaborationRequest.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query),
                is_active=True
            ).select_related('creator').prefetch_related(
                'collaborationrequestskill_set__skill'
            )[:20]
            
            results['collaborations'] = [
                {
                    'id': collab.id,
                    'title': collab.title,
                    'description': collab.description[:200] + '...' if collab.description and len(collab.description) > 200 else collab.description,
                    'is_active': collab.is_active,
                    'created_at': collab.created_at,
                    'creator': {
                        'id': collab.creator.id,
                        'username': collab.creator.username
                    },
                    'required_skills': [
                        {'id': crs.skill.id, 'name': crs.skill.name}
                        for crs in collab.collaborationrequestskill_set.all()[:5]
                    ]
                }
                for collab in collaborations
            ]
        
        return Response(results)

class AdvancedSearchView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        filters = request.data
        
        # Construire la requête pour les talents
        talent_profiles = TalentProfile.objects.all().select_related('user')
        
        # Filtrer par compétences
        if 'skills' in filters and filters['skills']:
            talent_profiles = talent_profiles.filter(
                talentprofileskill__skill__name__in=filters['skills']
            ).distinct()
        
        # Filtrer par pays
        if 'country' in filters and filters['country']:
            talent_profiles = talent_profiles.filter(
                user__profile__country__icontains=filters['country']
            )
        
        # Filtrer par école
        if 'school' in filters and filters['school']:
            talent_profiles = talent_profiles.filter(
                user__profile__school__icontains=filters['school']
            )
        
        # Filtrer par langue
        if 'language' in filters and filters['language']:
            talent_profiles = talent_profiles.filter(
                talentprofilelanguage__language__name__icontains=filters['language']
            ).distinct()
        
        # Filtrer par talent vérifié
        if filters.get('verified_only', False):
            talent_profiles = talent_profiles.filter(user__is_verified_talent=True)
        
        # Précharger les relations
        talent_profiles = talent_profiles.prefetch_related(
            'talentprofileskill_set__skill',
            'talentprofilelanguage_set__language'
        )[:50]
        
        results = []
        for tp in talent_profiles:
            profile = Profile.objects.filter(user=tp.user).first()
            results.append({
                'id': tp.user.id,
                'username': tp.user.username,
                'email': tp.user.email,
                'full_name': tp.user.get_full_name(),
                'is_verified_talent': tp.user.is_verified_talent,
                'profile': {
                    'country': profile.country if profile else None,
                    'school': profile.school if profile else None,
                    'specialization': profile.specialization if profile else None,
                    'bio': profile.bio[:200] + '...' if profile and profile.bio else None
                },
                'skills': [
                    {'id': tps.skill.id, 'name': tps.skill.name, 'category': tps.skill.category}
                    for tps in tp.talentprofileskill_set.all()
                ],
                'languages': [
                    {'id': tpl.language.id, 'name': tpl.language.name, 'level': tpl.language.level}
                    for tpl in tp.talentprofilelanguage_set.all()
                ]
            })
        
        return Response({
            'count': len(results),
            'results': results
        })
