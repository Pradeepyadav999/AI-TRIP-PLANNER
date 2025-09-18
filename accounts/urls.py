from django.urls import path
from .views import (
    UserRegisterView, UserLoginView, UserLogoutView,
    UserPasswordResetView, UserPasswordResetDoneView,
    UserPasswordResetConfirmView, UserPasswordResetCompleteView,
    profile_view, verify_email, edit_profile,
    feedback_list, feedback_create, feedback_detail, feedback_update, feedback_delete
)

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('verify/<int:user_id>/', verify_email, name='verify_email'),
    
    # Feedback URLs
    path('feedback/', feedback_list, name='feedback_list'),
    path('feedback/new/', feedback_create, name='feedback_create'),
    path('feedback/<int:pk>/', feedback_detail, name='feedback_detail'),
    path('feedback/<int:pk>/edit/', feedback_update, name='feedback_update'),
    path('feedback/<int:pk>/delete/', feedback_delete, name='feedback_delete'),
    
    # Password reset
    path('password-reset/', UserPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', UserPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', UserPasswordResetCompleteView.as_view(), name='password_reset_complete'),
] 