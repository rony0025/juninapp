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
from home.views import homeView, destinoView, getDistritos, getDestinos, lugarTuristicoView, favoritosView, getCoordenadas, getRecomendaciones, getRecursos, addFavoritos, addComentario, getCalificacion, updateCalificacion, borrarComentario, getComentarios
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', homeView, name='home'),
    path('destinos/', destinoView, name='destinos'),
    path('destinos/<str:nombre>/', lugarTuristicoView),
    path('mis-favoritos/', favoritosView, name='favoritos'),
    path('api/distritos/', getDistritos, name='api_distritos'),
    path('api/destinos/', getDestinos),
    path('api/coordenadas/', getCoordenadas),
    path('api/calificacion/', getCalificacion),
    path('api/recomendaciones/', getRecomendaciones),
    path('api/favoritos/', getRecursos),
    path('api/add/', addFavoritos),
    path('api/get/comentario/', getComentarios),
    path('api/add/comentario/', addComentario),
    path('api/delete/comentario/', borrarComentario),
    path('api/update/calificacion/', updateCalificacion),
    path('accounts/', include('allauth.urls')),
    path('logout', LogoutView.as_view(), name="logout"),
    
] +static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
