from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Idea, Feedback, Team, User

class RegistrationForm(UserCreationForm):
    
    class Meta:
        model = User
        fields = [ 'full_name', 'email', 'phone_number',
                  'password1', 'password2']


class IdeaForm(forms.ModelForm):
    class Meta:
        model = Idea
        fields = ['title', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
        }

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
        }
