from django.urls import include, path


app_name: str = "users"

urlpatterns = [
    path('m/', include('apis.users.mobile.urls', namespace='mobile')),
]
