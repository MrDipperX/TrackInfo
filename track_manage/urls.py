from django.urls import path
from .views import TrackHome, TrackLogin, logout_user, TrackUploadFile

urlpatterns = [
    path('', TrackHome.as_view(), name='home'),
    path('upload/', TrackUploadFile.as_view(), name='upload'),
    path('login/', TrackLogin.as_view(), name='login'),
    path('logout/', logout_user, name='logout')
]