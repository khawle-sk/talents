
from django.db import models
from users.models import User
from talents.models import Skill

class CollaborationRequest(models.Model):
    id = models.AutoField(primary_key=True)
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='creator_id'
    )
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'collaboration_collaborationrequest'
    
    def __str__(self):
        return self.title or f"Demande #{self.id}"

class CollaborationRequestSkill(models.Model):
    id = models.AutoField(primary_key=True)
    collaborationrequest = models.ForeignKey(
        CollaborationRequest,
        on_delete=models.CASCADE,
        db_column='collaborationrequest_id'
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        db_column='skill_id'
    )
    
    class Meta:
        db_table = 'collaboration_collaborationrequest_skills'
        unique_together = ('collaborationrequest', 'skill')
    
    def __str__(self):
        return f"{self.collaborationrequest.title} - {self.skill.name}"

class CollaborationApplication(models.Model):
    id = models.AutoField(primary_key=True)
    request = models.ForeignKey(
        CollaborationRequest,
        on_delete=models.CASCADE,
        db_column='request_id'
    )
    applicant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='applicant_id'
    )
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'collaboration_collaborationapplication'
        unique_together = ('request', 'applicant')
    
    def __str__(self):
        return f"Candidature de {self.applicant.username} pour {self.request.title}"