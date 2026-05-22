from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from django.contrib import messages
from .forms import RegistrationForm, IdeaForm, FeedbackForm
from .models import Idea, Feedback, User

class AppLoginView(LoginView):
    template_name = 'dashboard/login.html'

def logout_view(request):
    logout(request)
    return redirect('login')


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate until email is verified
            user.save()
            
            # Send verification email
            send_verification_email(request, user)
            messages.success(request, 'Registration successful! Please check your email to verify your account.')
            return redirect('email_verification_sent')
    else:
        form = RegistrationForm()
    return render(request, 'dashboard/register.html', {'form': form})


def send_verification_email(request, user):
    """Send email verification link to user"""
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    verification_url = request.build_absolute_uri(
        f'/verify-email/{uid}/{token}/'
    )
    
    subject = 'Verify your email address'
    message = f"""
    Hello {user.first_name},
    
    Please click the link below to verify your email address:
    
    {verification_url}
    
    This link will expire in 24 hours.
    
    Best regards,
    ScaleableHire Team
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


def email_verification_sent(request):
    """Display message after verification email is sent"""
    return render(request, 'dashboard/email_verification_sent.html')


def verify_email(request, uidb64, token):
    """Verify user email from token link"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Email verified successfully! You can now log in.')
        return redirect('login')
    else:
        messages.error(request, 'Email verification failed. The link may have expired.')
        return redirect('register')


def resend_verification_email(request):
    """Resend verification email to user"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email, is_active=False)
            send_verification_email(request, user)
            messages.success(request, 'Verification email has been resent. Please check your email.')
            return redirect('email_verification_sent')
        except User.DoesNotExist:
            messages.error(request, 'No unverified account found with this email address.')
    
    return render(request, 'dashboard/resend_verification.html')


@login_required(login_url='/login')
def dashboard_view(request):
    user = request.user
    ideas = Idea.objects.none()
    idea_and_feedbacks = []
    # manager_feedbacks = Feedback.objects.none()
    # teamlead_feedbacks = Feedback.objects.none()
    
    try:
        if user.is_manager:
            print('manager',)
            ideas = Idea.objects.all().order_by('-created_at')
            for idea in ideas:
                teamlead_fb = Feedback.objects.filter(idea=idea, author=idea.team.team_lead)
                manager_fb = Feedback.objects.filter(idea=idea, author=request.user)
                idea_and_feedbacks.append({
                    'idea': idea,
                    'teamlead_feedback': teamlead_fb if teamlead_fb.exists() else None,
                    'manager_feedback': manager_fb if manager_fb.exists() else None,
                })
            # teamlead_feedbacks = Feedback.objects.all()
        elif user.is_team_lead:
            print('team lead')
            try:
                manager = User.objects.filter(role=User.ROLE_MANAGER).first()
            except User.DoesNotExist:
                manager = None
            ideas = Idea.objects.filter(team=request.user.team.id).order_by('-created_at')
            for idea in ideas:
                teamlead_fb = Feedback.objects.filter(idea=idea, author=request.user)
                manager_fb = Feedback.objects.filter(idea=idea, author=manager)
                print(teamlead_fb, manager_fb)
                idea_and_feedbacks.append({
                    'idea': idea,
                    'teamlead_feedback': teamlead_fb if teamlead_fb.exists() else None,
                    'manager_feedback': manager_fb if manager_fb.exists() else None,
                })
            # print(ideas,request.user.team)
            # manager_feedbacks = Feedback.objects.filter(idea__team=User.team)
        else:
            print('staff')
            ideas = Idea.objects.filter(author=request.user).order_by('-created_at')
            for idea in ideas:
                # print(idea)
                teamlead_fb = Feedback.objects.filter(idea=idea, author=request.user.team.team_lead)
                # manager_fb = Feedback.objects.filter(idea=idea, author__is_manager=True)
                idea_and_feedbacks.append({
                    'idea': idea,
                    'teamlead_feedback': teamlead_fb if teamlead_fb.exists() else None,
                    # 'manager_feedback': manager_fb.first() if manager_fb.exists() else None,
                })
                print(idea_and_feedbacks)
    except:
       pass
    # print(idea_and_feedbacks)
    # print(ideas)
    return render(request, 'dashboard/dashboard.html', {
        # 'ideas': ideas,
        'idea_and_feedbacks': idea_and_feedbacks,
        'User': user,
    })

@login_required(login_url='/login')
def submit_idea(request):
    if request.method == 'POST':
        form = IdeaForm(request.POST)
        if form.is_valid():
            idea_obj = form.save(commit=False)
            idea_obj.author = request.user
            idea_obj.team = request.user.team
            idea_obj.save()
            return redirect('dashboard')
    else:
        form = IdeaForm()
    return render(request, 'dashboard/idea_form.html', {'form': form})

@login_required(login_url='/login')
def add_feedback(request, idea_id, feedback_id):
    idea_obj = get_object_or_404(Idea, pk=idea_id)
    if feedback_id:
        feedback_obj = get_object_or_404(Feedback, pk=feedback_id)
    User = request.user

    if not (User.is_manager or User.is_team_lead):
        return HttpResponseForbidden('Only managers and team leads can add feedback.')
    if User.is_team_lead and idea_obj.team != User.team:
        return HttpResponseForbidden('Team leads can only add feedback to their own team.')

    if request.method == 'POST':
        if feedback_id:
            form = FeedbackForm(request.POST, instance=feedback_obj)
        else:
            form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.idea = idea_obj
            feedback.author = request.user
            feedback.save()
            return redirect('dashboard')
    else:
        if feedback_id:
            form = FeedbackForm(instance=feedback_obj)
        else:
            form = FeedbackForm()

    return render(request, 'dashboard/feedback_form.html', 
                  {'form': form, 
                   'idea_obj': idea_obj,
                #    'feedback_id': feedback_id
                   })


@login_required(login_url='/login')
def delete_feedback(request, feedback_id):
    feedback = get_object_or_404(Feedback, pk=feedback_id)
    # if request.user != feedback.author:
        # return HttpResponseForbidden('You do not have permission to delete this feedback.')
    feedback.delete()
    return redirect('dashboard')

@login_required(login_url='/login')
def delete_idea(request, idea_id):
    idea = get_object_or_404(Idea, pk=idea_id)
    # if request.user != idea.author:
        # return HttpResponseForbidden('You do not have permission to delete this idea.')
    idea.delete()
    return redirect('dashboard')
