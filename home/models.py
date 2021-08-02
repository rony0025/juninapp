from django.db import models
from django.db.models.fields import BooleanField

from allauth.socialaccount.models import SocialAccount

# Create your models here.
class Provincia(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, blank=False, null=False)

    def __str__(self):
        return self.nombre
    
class Distrito(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, blank=False, null=False)
    provincia_id=models.ForeignKey(Provincia, on_delete=models.CASCADE, blank=False, null=False)

    def __str__(self):
        return self.nombre

class Categoria(models.Model):
    id = models.AutoField(primary_key = True)
    nombre = models.CharField(max_length=255, blank=False, null=False)
    tipo = BooleanField()

    def __str__(self):
        return self.nombre

class Recurso(models.Model):
    id = models.AutoField(primary_key = True)
    nombre = models.CharField(max_length=255, blank=False, null=False)
    image_URL = models.URLField(blank=True)
    subtitulo = models.CharField(max_length=400, blank=False, null=False)
    descripcion = models.TextField(max_length=1000, blank=True, null=True)
    puntuacion = models.BigIntegerField(default = 0, blank=False, null=False)
    distrito_id = models.ForeignKey(Distrito, on_delete=models.CASCADE, blank=False, null=False)
    categoria_id = models.ForeignKey(Categoria, on_delete=models.CASCADE, blank=False, null=False)

    def __str__(self):
        return self.nombre

class Coordenada(models.Model):
    id = models.AutoField(primary_key = True)
    recurso_id = models.OneToOneField(Recurso, on_delete=models.CASCADE, blank=False, null=False)
    latitud = models.FloatField(blank=True, null=True)
    longitud = models.FloatField(blank=True, null=True)

class Favorito(models.Model):
    id = models.AutoField(primary_key = True)
    usuario_id = models.ForeignKey(SocialAccount, on_delete=models.CASCADE, blank=False, null=False)
    recurso_id = models.ForeignKey(Recurso, related_name="favoritos", on_delete=models.CASCADE, blank=False, null=False)
    is_active = BooleanField()

class Calificacion(models.Model):
    id = models.AutoField(primary_key = True)
    criterio1 = models.IntegerField(default = 0, blank=False, null=False)
    criterio2 = models.IntegerField(default = 0, blank=False, null=False)
    criterio3 = models.IntegerField(default = 0, blank=False, null=False)
    criterio4 = models.IntegerField(default = 0, blank=False, null=False)
    criterio5 = models.IntegerField(default = 0, blank=False, null=False)
    usuario_id = models.ForeignKey(SocialAccount, on_delete=models.CASCADE, blank=False, null=False)
    recurso_id = models.ForeignKey(Recurso, on_delete=models.CASCADE, blank=False, null=False)

class Comentario(models.Model):
    id = models.AutoField(primary_key = True)
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField(max_length=1000, blank=True, null=True)
    usuario_id = models.ForeignKey(SocialAccount, on_delete=models.CASCADE, blank=False, null=False)
    recurso_id = models.ForeignKey(Recurso, on_delete=models.CASCADE, blank=False, null=False)