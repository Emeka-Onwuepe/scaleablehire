from django.contrib import admin
from .models import Team, Idea, Feedback


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    search_fields = ['name']

@admin.register(Idea)
class IdeaAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'team', 'created_at']
    list_filter = ['team', 'created_at']
    search_fields = ['title', 'content', 'author__full_name']

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['idea', 'author', 'created_at']
    list_filter = ['created_at']
    search_fields = ['idea__title', 'author__full_name', 'content']
