from django.urls import path

from . import views as authentication_views


app_name: str = "authentication"

urlpatterns: list = [
    path(
        'change-password',
        authentication_views.ChangePasswordAPIView.as_view(),
        name='change-password'
    ),
    path(
        'send-email-confirmation-link',
        authentication_views.SendEmailConfirmationLinkAPIView.as_view(),
        name='send-email-confirmation-link'
    ),
    path(
        'verify-email',
        authentication_views.VerifyEmailAPIView.as_view(),
        name='verify-email'
    ),
    path(
        'reset-password',
        authentication_views.ResetPasswordAPIView.as_view(),
        name='password-reset'
    ),
    path(
        'verify-password-reset-link',
        authentication_views.VerifyPasswordResetTokenAPIView.as_view(),
        name='verify-password-reset-link'
    ),
    path(
        'forgot-password',
        authentication_views.ForgotPasswordAPIView.as_view(),
        name='forgot-password'
    )
]
