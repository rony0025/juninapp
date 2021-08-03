from django.contrib import admin
from parler.admin import TranslatableAdmin
from .models import Provincia, Distrito, Categoria, Recurso, Coordenada, Favorito, Comentario, Calificacion

# Register your models here.
admin.site.register(Provincia)
admin.site.register(Distrito)
admin.site.register(Coordenada)
admin.site.register(Favorito)
admin.site.register(Comentario)
admin.site.register(Calificacion)

@admin.register(Categoria)
class ServiceAdmin(TranslatableAdmin):
  pass

@admin.register(Recurso)
class ServiceAdmin(TranslatableAdmin):
  pass