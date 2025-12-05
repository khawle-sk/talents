
from rest_framework import serializers
from .models import CollaborationRequest, CollaborationApplication, CollaborationRequestSkill
from talents.serializers import SkillSerializer
from users.serializers import UserSerializer

class CollaborationRequestSkillSerializer(serializers.ModelSerializer):
    skill = SkillSerializer(read_only=True)
    
    class Meta:
        model = CollaborationRequestSkill
        fields = ('id', 'skill')

class CollaborationRequestSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    required_skills = serializers.SerializerMethodField()
    applications_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CollaborationRequest
        fields = '__all__'
        read_only_fields = ('creator', 'created_at')
    
    def get_required_skills(self, obj):
        skills = obj.collaborationrequestskill_set.all()
        return CollaborationRequestSkillSerializer(skills, many=True).data
    
    def get_applications_count(self, obj):
        return obj.collaborationapplication_set.count()

class CollaborationRequestCreateSerializer(serializers.ModelSerializer):
    skill_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = CollaborationRequest
        fields = ('title', 'description', 'skill_ids')
    
    def create(self, validated_data):
        skill_ids = validated_data.pop('skill_ids', [])
        request = CollaborationRequest.objects.create(**validated_data)
        
        # Ajouter les compétences
        from talents.models import Skill
        for skill_id in skill_ids:
            try:
                skill = Skill.objects.get(id=skill_id)
                CollaborationRequestSkill.objects.create(
                    collaborationrequest=request,
                    skill=skill
                )
            except Skill.DoesNotExist:
                pass
        
        return request

class CollaborationApplicationSerializer(serializers.ModelSerializer):
    applicant = UserSerializer(read_only=True)
    request = CollaborationRequestSerializer(read_only=True)
    
    class Meta:
        model = CollaborationApplication
        fields = '__all__'
        read_only_fields = ('applicant', 'request', 'created_at', 'accepted')