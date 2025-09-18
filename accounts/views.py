from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordResetView, 
    PasswordResetDoneView, PasswordResetConfirmView, 
    PasswordResetCompleteView
)
from django.contrib.auth.models import User
from .forms import UserRegistrationForm, UserLoginForm, UserPasswordResetForm, UserSetPasswordForm, ProfileEditForm, FeedbackForm
from .models import UserProfile, Feedback
from django.utils import timezone

# Create your views here.

class UserRegisterView(FormView):
    template_name = 'accounts/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        user = form.save()
        
        # Send verification email (you would implement this for production)
        if not settings.DEBUG:
            # Send verification email in production
            send_mail(
                'Verify your Travel Explorer account',
                f'Thank you for registering. Please verify your account by clicking this link: {self.request.build_absolute_uri("/verify/" + str(user.id))}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        
        messages.success(self.request, 'Registration successful! Please log in.')
        return super().form_valid(form)

class UserLoginView(LoginView):
    template_name = 'accounts/login.html'
    form_class = UserLoginForm
    
    def form_valid(self, form):
        remember_me = self.request.POST.get('remember_me', False)
        if not remember_me:
            # Session expires when user closes browser
            self.request.session.set_expiry(0)
        
        # Check if user is verified
        user = form.get_user()
        if not user.profile.is_verified:
            messages.error(self.request, 'Please verify your email before logging in.')
            return self.form_invalid(form)
            
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('home')

class UserLogoutView(LogoutView):
    next_page = reverse_lazy('login')

class UserPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    form_class = UserPasswordResetForm
    success_url = reverse_lazy('password_reset_done')
    email_template_name = 'accounts/password_reset_email.html'

class UserPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'

class UserPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    form_class = UserSetPasswordForm
    success_url = reverse_lazy('password_reset_complete')

class UserPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'

@login_required
def profile_view(request):
    """View for user profile"""
    context = {}
    
    # Process travel history
    if request.user.profile.travel_history:
        try:
            import json
            # Parse travel history from JSON
            travel_history = json.loads(request.user.profile.travel_history)
            context['travel_history'] = travel_history
        except json.JSONDecodeError:
            # Handle legacy comma-separated format
            travel_places = [place.strip() for place in request.user.profile.travel_history.split(',')]
            context['travel_places'] = travel_places
    
    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile(request):
    """View for editing user profile"""
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user.profile, user=request.user)
        if form.is_valid():
            form.save(user=request.user)
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=request.user.profile, user=request.user)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})

def verify_email(request, user_id):
    """View to verify user email"""
    try:
        user = User.objects.get(id=user_id)
        user.profile.is_verified = True
        user.profile.save()
        messages.success(request, 'Email verified! You can now log in.')
    except User.DoesNotExist:
        messages.error(request, 'Invalid verification link')
    
    return redirect('login')

def feedback_list(request):
    """View to list all feedback, with user's own feedback highlighted"""
    # Get all published feedback
    all_feedback = Feedback.objects.all()
    
    # Get current user's feedback if logged in
    user_feedback = []
    if request.user.is_authenticated:
        user_feedback = Feedback.objects.filter(user=request.user)
    
    # Get all places and hotels for displaying entity names
    from hotels.models import Place, Hotel
    places = Place.objects.all()
    hotels = Hotel.objects.all()
    
    context = {
        'all_feedback': all_feedback,
        'user_feedback': user_feedback,
        'places': places,
        'hotels': hotels
    }
    return render(request, 'accounts/feedback_list.html', context)

@login_required
def feedback_create(request):
    """View to create new feedback"""
    if request.method == 'POST':
        form = FeedbackForm(request.POST, request.FILES)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            # Auto-generate a subject based on what is being reviewed
            entity_name = ""
            if feedback.entity_type == 'destination' and feedback.entity_id:
                try:
                    from hotels.models import Place
                    place = Place.objects.get(id=feedback.entity_id)
                    entity_name = place.name
                except:
                    pass
            elif feedback.entity_type == 'hotel' and feedback.entity_id:
                try:
                    from hotels.models import Hotel
                    hotel = Hotel.objects.get(id=feedback.entity_id)
                    entity_name = hotel.name
                except:
                    pass
            
            if entity_name:
                feedback.subject = f"Review of {entity_name}"
            else:
                feedback.subject = f"Review of {feedback.get_entity_type_display()}"
                
            feedback.save()
            messages.success(request, 'Your review has been submitted. Thank you!')
            return redirect('feedback_list')
    else:
        # Pre-populate entity type if specified in URL
        entity_type = request.GET.get('entity_type', '')
        entity_id = request.GET.get('entity_id', '')
        
        initial_data = {}
        if entity_type and entity_id:
            initial_data['entity_type'] = entity_type
            if entity_type == 'destination':
                try:
                    from hotels.models import Place
                    initial_data['place'] = Place.objects.get(id=entity_id)
                except:
                    pass
            elif entity_type == 'hotel':
                try:
                    from hotels.models import Hotel
                    initial_data['hotel'] = Hotel.objects.get(id=entity_id)
                except:
                    pass
                
        form = FeedbackForm(initial=initial_data)
    
    return render(request, 'accounts/feedback_form.html', {'form': form, 'title': 'Submit Review'})

@login_required
def feedback_detail(request, pk):
    """View to see feedback details"""
    feedback = get_object_or_404(Feedback, pk=pk, user=request.user)
    return render(request, 'accounts/feedback_detail.html', {'feedback': feedback})

@login_required
def feedback_update(request, pk):
    """View to update feedback"""
    feedback = get_object_or_404(Feedback, pk=pk, user=request.user)
    
    # Only allow updating pending feedback
    if feedback.status != 'pending':
        messages.error(request, 'You can only edit feedback that has not been reviewed yet.')
        return redirect('feedback_detail', pk=pk)
    
    if request.method == 'POST':
        form = FeedbackForm(request.POST, request.FILES, instance=feedback)
        if form.is_valid():
            updated_feedback = form.save(commit=False)
            
            # Auto-generate a subject based on what is being reviewed
            entity_name = ""
            if updated_feedback.entity_type == 'destination' and updated_feedback.entity_id:
                try:
                    from hotels.models import Place
                    place = Place.objects.get(id=updated_feedback.entity_id)
                    entity_name = place.name
                except:
                    pass
            elif updated_feedback.entity_type == 'hotel' and updated_feedback.entity_id:
                try:
                    from hotels.models import Hotel
                    hotel = Hotel.objects.get(id=updated_feedback.entity_id)
                    entity_name = hotel.name
                except:
                    pass
            
            if entity_name:
                updated_feedback.subject = f"Review of {entity_name}"
            else:
                updated_feedback.subject = f"Review of {updated_feedback.get_entity_type_display()}"
                
            updated_feedback.save()
            messages.success(request, 'Your review has been updated.')
            return redirect('feedback_detail', pk=pk)
    else:
        # Prepare initial data for the form
        initial_data = {}
        
        if feedback.entity_type == 'destination':
            try:
                from hotels.models import Place
                initial_data['place'] = Place.objects.get(id=feedback.entity_id)
            except:
                pass
        elif feedback.entity_type == 'hotel':
            try:
                from hotels.models import Hotel
                initial_data['hotel'] = Hotel.objects.get(id=feedback.entity_id)
            except:
                pass
            
        form = FeedbackForm(instance=feedback, initial=initial_data)
    
    return render(request, 'accounts/feedback_form.html', {
        'form': form, 
        'title': 'Update Review',
        'is_update': True
    })

@login_required
def feedback_delete(request, pk):
    """View to delete feedback"""
    feedback = get_object_or_404(Feedback, pk=pk, user=request.user)
    
    # Only allow deleting pending feedback
    if feedback.status != 'pending':
        messages.error(request, 'You can only delete feedback that has not been reviewed yet.')
        return redirect('feedback_detail', pk=pk)
    
    if request.method == 'POST':
        feedback.delete()
        messages.success(request, 'Your feedback has been deleted.')
        return redirect('feedback_list')
    
    return render(request, 'accounts/feedback_confirm_delete.html', {'feedback': feedback})
