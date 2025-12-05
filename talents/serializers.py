
from rest_framework import serializers
from .models import (
    Skill, Language, Project, TalentProfile,
    TalentProfileSkill, TalentProfileLanguage,
    TalentProfileFeaturedProject, TalentValidation
)
from users.serializers import UserSerializer


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'


class LanguageSerializer(serializers.ModelSerializer):
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    
    class Meta:
        model = Language
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ('user', 'created_at')


class TalentProfileSkillSerializer(serializers.ModelSerializer):
    skill = SkillSerializer(read_only=True)
    
    class Meta:
        model = TalentProfileSkill
        fields = ('id', 'skill')


class TalentProfileLanguageSerializer(serializers.ModelSerializer):
    language = LanguageSerializer(read_only=True)
    
    class Meta:
        model = TalentProfileLanguage
        fields = ('id', 'language')


class TalentProfileFeaturedProjectSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(read_only=True)
    
    class Meta:
        model = TalentProfileFeaturedProject
        fields = ('id', 'project')


class TalentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    skills_count = serializers.SerializerMethodField()
    languages_count = serializers.SerializerMethodField()
    projects_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TalentProfile
        fields = [
            'id', 'user', 'bio', 'avatar', 'created_at', 'updated_at',
            'skills_count', 'languages_count', 'projects_count'
        ]
        read_only_fields = ('user', 'updated_at')
    
    def get_skills_count(self, obj):
        return obj.talentprofileskill_set.count()
    
    def get_languages_count(self, obj):
        return obj.talentprofilelanguage_set.count()
    
    def get_projects_count(self, obj):
        return obj.talentprofilefeaturedproject_set.count()


class TalentProfileDetailSerializer(TalentProfileSerializer):
    skills = TalentProfileSkillSerializer(
        many=True, read_only=True, source='talentprofileskill_set'
    )
    languages = TalentProfileLanguageSerializer(
        many=True, read_only=True, source='talentprofilelanguage_set'
    )
    featured_projects = TalentProfileFeaturedProjectSerializer(
        many=True, read_only=True, source='talentprofilefeaturedproject_set'
    )
    
    class Meta(TalentProfileSerializer.Meta):
        # On ajoute les champs relationnels à la liste des champs existants
        fields = list(TalentProfileSerializer.Meta.fields) + [
            'skills', 'languages', 'featured_projects'
        ]


class TalentValidationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    validated_by = UserSerializer(read_only=True)
    
    class Meta:
        model = TalentValidation
        fields = '__all__'
        read_only_fields = ('validated_by', 'validated_at')
