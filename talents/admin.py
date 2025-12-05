from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import (
    Skill, Language, Project, TalentProfile,
    TalentProfileSkill, TalentProfileLanguage,
    TalentProfileFeaturedProject, TalentValidation
)

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    search_fields = ('name', 'category')
    list_filter = ('category',)

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'level')
    search_fields = ('name',)
    list_filter = ('level',)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at')
    search_fields = ('title', 'user__username')
    list_filter = ('created_at',)

class TalentProfileSkillInline(admin.TabularInline):
    model = TalentProfileSkill
    extra = 1

class TalentProfileLanguageInline(admin.TabularInline):
    model = TalentProfileLanguage
    extra = 1

class TalentProfileFeaturedProjectInline(admin.TabularInline):
    model = TalentProfileFeaturedProject
    extra = 1

@admin.register(TalentProfile)
class TalentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'updated_at')
    search_fields = ('user__username', 'user__email')
    inlines = [TalentProfileSkillInline, TalentProfileLanguageInline, TalentProfileFeaturedProjectInline]

@admin.register(TalentValidation)
class TalentValidationAdmin(admin.ModelAdmin):
    list_display = ('user', 'validated_by', 'validated_at')
    search_fields = ('user__username', 'validated_by__username')
    list_filter = ('validated_at',)



    