from django.contrib import admin
from .models import Provincia, Distrito, Categoria, Recurso, Coordenada, Favorito, Comentario, Calificacion

# Register your models here.
admin.site.register(Provincia)
admin.site.register(Distrito)
admin.site.register(Categoria)
admin.site.register(Recurso)
admin.site.register(Coordenada)
admin.site.register(Favorito)
admin.site.register(Comentario)
admin.site.register(Calificacion)