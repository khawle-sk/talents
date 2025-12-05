from django.contrib import admin

# Register your models here.

from .models import CollaborationRequest, CollaborationRequestSkill, CollaborationApplication

class CollaborationRequestSkillInline(admin.TabularInline):
    model = CollaborationRequestSkill
    extra = 1

class CollaborationApplicationInline(admin.TabularInline):
    model = CollaborationApplication
    extra = 1

@admin.register(CollaborationRequest)
class CollaborationRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'creator__username', 'description')
    inlines = [CollaborationRequestSkillInline, CollaborationApplicationInline]

@admin.register(CollaborationApplication)
class CollaborationApplicationAdmin(admin.ModelAdmin):
    list_display = ('request', 'applicant', 'created_at', 'accepted')
    list_filter = ('accepted', 'created_at')
    search_fields = ('request__title', 'applicant__username', 'message')