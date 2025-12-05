from django.shortcuts import render

# Create your views here.


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Count, Q
from collections import Counter
from users.models import Profile
from talents.models import Skill, TalentProfile, Project
from collaboration.models import CollaborationRequest

class TalentCloudView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        # Récupérer toutes les compétences avec leur nombre d'occurrences
        skills = Skill.objects.annotate(
            talent_count=Count('talentprofileskill')
        ).filter(talent_count__gt=0).order_by('-talent_count')[:50]
        
        if not skills:
            return Response({'skills': []})
        
        max_count = skills[0].talent_count
        
        cloud_data = []
        for skill in skills:
            # Calculer la taille relative (12-48px)
            size = 12 + (skill.talent_count / max_count) * 36
            
            cloud_data.append({
                'id': skill.id,
                'name': skill.name,
                'category': skill.category or 'Autre',
                'count': skill.talent_count,
                'size': round(size),
                'percentage': round((skill.talent_count / max_count) * 100)
            })
        
        return Response({'skills': cloud_data})

class TalentMapView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        # Récupérer les talents par pays
        talent_map = Profile.objects.filter(
            country__isnull=False,
            user__talentprofile__isnull=False
        ).values('country').annotate(
            talent_count=Count('user')
        ).order_by('-talent_count')
        
        countries_data = []
        for item in talent_map:
            # Obtenir quelques talents de ce pays
            talents_in_country = Profile.objects.filter(
                country=item['country'],
                user__talentprofile__isnull=False
            ).select_related('user')[:5]
            
            talents_list = []
            for profile in talents_in_country:
                talents_list.append({
                    'id': profile.user.id,
                    'username': profile.user.username,
                    'full_name': profile.user.get_full_name(),
                    'is_verified_talent': profile.user.is_verified_talent,
                    'skills': list(profile.user.talentprofile.talentprofileskill_set
                                  .select_related('skill')
                                  .values('skill__name', 'skill__category')[:3])
                })
            
            countries_data.append({
                'country': item['country'],
                'talent_count': item['talent_count'],
                'talents': talents_list
            })
        
        return Response({'countries': countries_data})

class StatsView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        from users.models import User
        from talents.models import TalentProfile, Project
        from collaboration.models import CollaborationRequest
        
        stats = {
            'total_users': User.objects.count(),
            'verified_talents': User.objects.filter(is_verified_talent=True).count(),
            'total_skills': Skill.objects.count(),
            'skills_with_talents': Skill.objects.annotate(
                talent_count=Count('talentprofileskill')
            ).filter(talent_count__gt=0).count(),
            'total_projects': Project.objects.count(),
            'active_collaborations': CollaborationRequest.objects.filter(is_active=True).count(),
            'talent_profiles': TalentProfile.objects.count(),
        }
        
        # Top compétences
        top_skills = Skill.objects.annotate(
            talent_count=Count('talentprofileskill')
        ).filter(talent_count__gt=0).order_by('-talent_count')[:10].values(
            'id', 'name', 'category', 'talent_count'
        )
        
        # Top pays
        top_countries = Profile.objects.filter(
            country__isnull=False,
            user__talentprofile__isnull=False
        ).values('country').annotate(
            count=Count('user')
        ).order_by('-count')[:10]
        
        stats['top_skills'] = list(top_skills)
        stats['top_countries'] = list(top_countries)
        
        # Collaborations récentes
        recent_collaborations = CollaborationRequest.objects.filter(
            is_active=True
        ).order_by('-created_at')[:5].values(
            'id', 'title', 'created_at', 'creator__username'
        )
        
        stats['recent_collaborations'] = list(recent_collaborations)
        
        return Response(stats)
