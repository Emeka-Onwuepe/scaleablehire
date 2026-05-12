from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('login/', views.AppLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('idea/new/', views.submit_idea, name='submit_idea'),
    path('feedback/<int:idea_id>/<int:feedback_id>/', views.add_feedback, name='add_feedback'),
    path('delect_feedback/<int:feedback_id>/', views.delete_feedback, name='delete_feedback'),
    path('delect_idea/<int:idea_id>/', views.delete_idea, name='delete_idea'),


]