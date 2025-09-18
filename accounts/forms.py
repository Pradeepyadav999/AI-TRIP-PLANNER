from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import UserProfile, Feedback
from hotels.models import Place, Hotel

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))
    
    # Profile fields
    gender = forms.ChoiceField(choices=UserProfile.GENDER_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    preferred_language = forms.ChoiceField(choices=UserProfile.LANGUAGE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    travel_preferences = forms.ChoiceField(choices=UserProfile.TRAVEL_PREFERENCES, widget=forms.Select(attrs={'class': 'form-control'}))
    budget_range = forms.ChoiceField(choices=UserProfile.BUDGET_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    profile_picture = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email is already registered")
        return email
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            # Create a new profile
            try:
                profile, created = UserProfile.objects.get_or_create(user=user)
                profile.full_name = f"{self.cleaned_data['first_name']} {self.cleaned_data['last_name']}"
                profile.gender = self.cleaned_data['gender']
                profile.date_of_birth = self.cleaned_data['date_of_birth']
                profile.preferred_language = self.cleaned_data['preferred_language']
                profile.travel_preferences = self.cleaned_data['travel_preferences']
                profile.budget_range = self.cleaned_data['budget_range']
                profile.is_verified = True
                
                if 'profile_picture' in self.cleaned_data and self.cleaned_data['profile_picture']:
                    profile.profile_picture = self.cleaned_data['profile_picture']
                    
                profile.save()
            except Exception as e:
                print(f"Error creating profile: {e}")
            
        return user

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username or Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    
    def clean_username(self):
        """Allow login with email"""
        username = self.cleaned_data.get('username')
        # Check if the input is an email
        if '@' in username:
            try:
                user = User.objects.get(email=username)
                return user.username
            except User.DoesNotExist:
                pass
        return username

class UserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))

class UserSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm New Password'}))

class ProfileEditForm(forms.ModelForm):
    """Form for editing user profile"""
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    
    class Meta:
        model = UserProfile
        fields = [
            'gender', 'date_of_birth', 'preferred_language', 
            'travel_preferences', 'budget_range', 'profile_picture'
        ]
        widgets = {
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'preferred_language': forms.Select(attrs={'class': 'form-control'}),
            'travel_preferences': forms.Select(attrs={'class': 'form-control'}),
            'budget_range': forms.Select(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'})
        }
        
    def __init__(self, *args, **kwargs):
        """Initialize with user data"""
        user = kwargs.pop('user', None)
        super(ProfileEditForm, self).__init__(*args, **kwargs)
        
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            
    def save(self, user=None, commit=True):
        """Save both user and profile data"""
        profile = super(ProfileEditForm, self).save(commit=False)
        
        if user:
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            profile.full_name = f"{self.cleaned_data['first_name']} {self.cleaned_data['last_name']}"
            
            if commit:
                user.save()
                profile.save()
                
        return profile 

class FeedbackForm(forms.ModelForm):
    """Form for submitting feedback"""
    # Dynamic selection fields for entities
    place = forms.ModelChoiceField(
        queryset=Place.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select a destination'}),
        empty_label="Select a destination"
    )
    
    hotel = forms.ModelChoiceField(
        queryset=Hotel.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select a hotel'}),
        empty_label="Select a hotel"
    )
    
    class Meta:
        model = Feedback
        fields = ['message', 'rating', 'entity_type', 'photos']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your Review', 'rows': 5}),
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'entity_type': forms.Select(attrs={'class': 'form-control', 'placeholder': 'What are you reviewing?'}),
            'photos': forms.FileInput(attrs={'class': 'form-control'})
        }
    
    def clean(self):
        cleaned_data = super().clean()
        entity_type = cleaned_data.get('entity_type')
        
        # Validate that the correct entity is selected based on entity_type
        if entity_type == 'destination':
            if not cleaned_data.get('place'):
                self.add_error('place', 'Please select a destination')
        elif entity_type == 'hotel':
            if not cleaned_data.get('hotel'):
                self.add_error('hotel', 'Please select a hotel')
                
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Set the entity_id based on the selected entity
        if instance.entity_type == 'destination' and self.cleaned_data.get('place'):
            instance.entity_id = self.cleaned_data['place'].id
        elif instance.entity_type == 'hotel' and self.cleaned_data.get('hotel'):
            instance.entity_id = self.cleaned_data['hotel'].id
            
        if commit:
            instance.save()
        return instance 