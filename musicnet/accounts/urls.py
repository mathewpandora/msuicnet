from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    ProfileView,
    UpdateProfileView,
    ChangePasswordView,
    DeleteAccountView,
    FollowUserView,
    verify_email
)

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('profile/', ProfileView.as_view()),
    path('profile/update/', UpdateProfileView.as_view()),
    path('change-password/', ChangePasswordView.as_view()),
    path('delete-account/', DeleteAccountView.as_view()),
    path('users/<int:user_id>/follow/', FollowUserView.as_view(), name='user-follow'),
    path('verify-email/', verify_email, name='verify-email'),

]
