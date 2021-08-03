from django.db import models
from django.db.models.fields import BooleanField
from django.utils.translation import ugettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields

from allauth.socialaccount.models import SocialAccount

# Create your models here.
class Provincia(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, blank=False, null=False, verbose_name=_('Nombre'))

    class Meta:
        verbose_name = _('Provincia')
        verbose_name_plural = _('Provincias')

    def _str_(self):
        return self.nombre
    
class Distrito(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, blank=False, null=False, verbose_name=_('Nombre'))
    provincia_id=models.ForeignKey(Provincia, on_delete=models.CASCADE, blank=False, null=False)

    class Meta:
        verbose_name = _('Distrito')
        verbose_name_plural = _('Distritos')

    def _str_(self):
        return self.nombre

class Categoria(TranslatableModel):
    id = models.AutoField(primary_key = True)
    translations = TranslatedFields(
        nombre = models.CharField(max_length=255, blank=False, null=False, verbose_name=_('Nombre'))
    )
    tipo = BooleanField()

    class Meta:
        verbose_name = _('Categoría')
        verbose_name_plural = _('Categorías')

    def _str_(self):
        return self.nombre

class Recurso(TranslatableModel):
    id = models.AutoField(primary_key = True)
    nombre = models.CharField(max_length=255, blank=False, null=False, verbose_name=_('Nombre'))
    image_URL = models.URLField(blank=True, verbose_name=_('Dirección de la imagen'))
    translations = TranslatedFields(
        subtitulo = models.CharField(max_length=400, blank=False, null=False, verbose_name=_('Subtítulo')),
        descripcion = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_('Descripción'))
    )
    puntuacion = models.BigIntegerField(default = 0, blank=False, null=False, verbose_name=_('Puntuación'))
    distrito_id = models.ForeignKey(Distrito, on_delete=models.CASCADE, blank=False, null=False)
    categoria_id = models.ForeignKey(Categoria, on_delete=models.CASCADE, blank=False, null=False)

    class Meta:
        verbose_name = _('Recurso Turistico')
        verbose_name_plural = _('Recursos Turisticos')

    def _str_(self):
        return self.nombre

class Coordenada(models.Model):
    id = models.AutoField(primary_key = True)
    recurso_id = models.OneToOneField(Recurso, on_delete=models.CASCADE, blank=False, null=False)
    latitud = models.FloatField(blank=True, null=True, verbose_name=_('Latitud'))
    longitud = models.FloatField(blank=True, null=True, verbose_name=_('Longitud'))

class Favorito(models.Model):
    id = models.AutoField(primary_key = True)
    usuario_id = models.ForeignKey(SocialAccount, on_delete=models.CASCADE, blank=False, null=False)
    recurso_id = models.ForeignKey(Recurso, related_name="favoritos", on_delete=models.CASCADE, blank=False, null=False)
    is_active = BooleanField()

class Calificacion(models.Model):
    id = models.AutoField(primary_key = True)
    accesibilidad = models.IntegerField(default = 0, blank=False, null=False, verbose_name=_('Puntaje en accesibilidad'))
    aforo = models.IntegerField(default = 0, blank=False, null=False, verbose_name=_('Puntaje en aforo'))
    eco_amigable = models.IntegerField(default = 0, blank=False, null=False, verbose_name=_('Puntaje en eco amigable'))
    educativo = models.IntegerField(default = 0, blank=False, null=False, verbose_name=_('Puntaje en educativo'))
    recreacional = models.IntegerField(default = 0, blank=False, null=False, verbose_name=_('Puntaje en recreacional'))
    usuario_id = models.ForeignKey(SocialAccount, on_delete=models.CASCADE, blank=False, null=False)
    recurso_id = models.ForeignKey(Recurso, on_delete=models.CASCADE, blank=False, null=False)

class Comentario(models.Model):
    id = models.AutoField(primary_key = True)
    fecha = models.DateTimeField(auto_now_add=True, verbose_name=_('Fecha de creación'))
    descripcion = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_('Contenido'))
    usuario_id = models.ForeignKey(SocialAccount, on_delete=models.CASCADE, blank=False, null=False)
    recurso_id = models.ForeignKey(Recurso, on_delete=models.CASCADE, blank=False, null=False)