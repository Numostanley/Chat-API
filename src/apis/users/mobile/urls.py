from django.urls import path

from . import views as mobile_views


app_name: str = "mobile"

urlpatterns: list = [
    path(
        'signup',
        mobile_views.SignupAPIView.as_view(),
        name='signup'
    ),
    path(
        'user_detail',
        mobile_views.UserDetailAPIView.as_view(),
        name='user_detail'
    )
]
