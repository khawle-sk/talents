
from django.db import models
from users.models import User

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        db_table = 'talents_skill'
    
    def __str__(self):
        return self.name

class Language(models.Model):
    name = models.CharField(max_length=100)
    level = models.CharField(max_length=2)
    
    class Meta:
        db_table = 'talents_language'
        unique_together = ('name', 'level')
    
    def __str__(self):
        return f"{self.name} ({self.level})"

class Project(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='user_id'
    )
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    link = models.CharField(max_length=300, blank=True, null=True)
    created_at = models.DateField(auto_now_add=True)
    
    class Meta:
        db_table = 'talents_project'
    
    def __str__(self):
        return self.title or f"Projet #{self.id}"

class TalentProfile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        db_column='user_id'
    )
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'talents_talentprofile'
    
    def __str__(self):
        return f"Profil Talent de {self.user.username}"

class TalentProfileSkill(models.Model):
    id = models.AutoField(primary_key=True)
    talentprofile = models.ForeignKey(
        TalentProfile,
        on_delete=models.CASCADE,
        db_column='talentprofile_id'
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        db_column='skill_id'
    )
    
    class Meta:
        db_table = 'talents_talentprofile_skills'
        unique_together = ('talentprofile', 'skill')
    
    def __str__(self):
        return f"{self.talentprofile.user.username} - {self.skill.name}"

class TalentProfileLanguage(models.Model):
    id = models.AutoField(primary_key=True)
    talentprofile = models.ForeignKey(
        TalentProfile,
        on_delete=models.CASCADE,
        db_column='talentprofile_id'
    )
    language = models.ForeignKey(
        Language,
        on_delete=models.CASCADE,
        db_column='language_id'
    )
    
    class Meta:
        db_table = 'talents_talentprofile_languages'
        unique_together = ('talentprofile', 'language')
    
    def __str__(self):
        return f"{self.talentprofile.user.username} - {self.language.name}"

class TalentProfileFeaturedProject(models.Model):
    id = models.AutoField(primary_key=True)
    talentprofile = models.ForeignKey(
        TalentProfile,
        on_delete=models.CASCADE,
        db_column='talentprofile_id'
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        db_column='project_id'
    )
    
    class Meta:
        db_table = 'talents_talentprofile_featured_projects'
        unique_together = ('talentprofile', 'project')
    
    def __str__(self):
        return f"{self.talentprofile.user.username} - {self.project.title}"

class TalentValidation(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='user_id'
    )
    validated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        db_column='validated_by',
        related_name='validations_given'
    )
    comment = models.TextField(blank=True, null=True)
    validated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'talents_talentvalidation'
    
    def __str__(self):
        validator = self.validated_by.username if self.validated_by else "System"
        return f"Validation de {self.user.username} par {validator}"