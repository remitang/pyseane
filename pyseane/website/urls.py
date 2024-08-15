from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('register', register, name='register'),
    path('login', login_user, name='login_user'),
    path('logout', logout_user, name='logout_user'),
    path('cgu', cgu, name='cgu'),
    path('campagne', campagne_register, name='campagne_register'),
    path('campagnes/<uuid:id>', detail_campagne, name='detail_campagne'),
    path('panel', panel, name='panel'),
    path('panel/email', email, name='email'),
    path('panel/campagnes', gestion_campagne, name='gestion_campagne'),
    # Add more URLs as needed
]
