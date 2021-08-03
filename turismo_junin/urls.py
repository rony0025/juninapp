"""turimoJunin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from home.views import *

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('accounts/', include('allauth.urls')),
    path('admin/', admin.site.urls),
    path('', homeView, name='home'),
    path('destinos/', destinoView, name='destinos'),
    path('cultura/', culturaView, name='cultura'),
    path('recurso-turistico/<str:nombre>/', recursoTuristicoView),
    path('mis-favoritos/', favoritosView, name='favoritos'),
    
    path('api/recursos/tangibles/', filteredResourcesTangiblesJson),
    path('api/recursos/intangibles/', filteredResourcesIntangiblesJson),
    
    path('api/get/distritos/', distritosJson, name='api_distritos'),
    path('api/get/coordenadas/', coordenadasJson),
    path('api/get/recomendaciones/', recommendationsJson),

    path('api/get/favoritos/', getFavoritos),
    path('api/update/favoritos/', updateFavoritos),

    path('api/get/calificacion/', getCalificacion),
    path('api/update/calificacion/', updateCalificacion),

    path('api/get/comentario/', getComentarios),
    path('api/add/comentario/', addComentario),
    path('api/delete/comentario/', deleteComentario),
    path('logout', LogoutView.as_view(), name="logout"),
    
]
