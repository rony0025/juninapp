from django.test import TestCase

from .views import *
from .models import *
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User

# Create your tests here.

""" Testing del requerimieto RF06 () """

class RecommendedResource_TestCase(TestCase):
  fixtures = ["all.json"]
  
  def setUp(self):
    pass

  def test_user_auth_recommendationsJson(self):
    userSocial = SocialAccount.objects.first()
    self.client.force_login(userSocial.user)
    response = self.client.get("/api/recomendaciones/")
    response_status = response.status_code
    response_json = response.json()
    self.assertEqual(response.status_code, 200)
    self.assertIsInstance(response_json, list)
    for recurso in response_json:
      self.assertIsInstance(recurso, dict)
      self.assertIsInstance(recurso.get("image"), str)
      self.assertIsInstance(recurso.get("nombre"), str)
      self.assertIsInstance(recurso.get("provincia"), str)
      self.assertIsInstance(recurso.get("corazon"), dict)
      self.assertIsInstance(recurso.get("corazon").get("contador"), int)
      self.assertIsInstance(recurso.get("corazon").get("marcado"), bool)

  def test_user_noauth_recommendationsJson(self):
    response = self.client.get("/api/recomendaciones/")
    response_status = response.status_code
    response_json = response.json()
    for recurso in response_json:
      self.assertEqual(response.status_code, 200)
      self.assertIsInstance(response_json, list)
      self.assertIsInstance(recurso, dict)
      self.assertIsInstance(recurso.get("image"), str)
      self.assertIsInstance(recurso.get("nombre"), str)
      self.assertIsInstance(recurso.get("provincia"), str)
      self.assertIsInstance(recurso.get("corazon"), dict)
      self.assertIsInstance(recurso.get("corazon").get("contador"), int)
      self.assertIsInstance(recurso.get("corazon").get("marcado"), bool)

  def test_userSocial_auth_getRecommendedResources(self):
    userSocial = SocialAccount.objects.first()
    self.client.force_login(userSocial.user)
    recommendedResources = getRecommendedResources(userSocial, 5)
    self.assertEqual(0 <= len(recommendedResources) and len(recommendedResources) <= 5, True)
    for recurso in recommendedResources:
      puntaje = Recurso.objects.order_by('-puntuacion')
      self.assertEqual(recurso["corazon"]["contador"], puntaje)

  def test_userSocial_no_auth_getRecommendedResources(self):
    respuestaEsperada = [{'image': 'imagen', 'nombre': 'Bosque De Ocopilla', 'provincia': 'Huancayo', 'categoria': 'Sitios Naturales', 'corazon': {'contador': 0, 'marcado': False}}, {'image': 'imagen', 'nombre': 'Estación Ferroviaria De Chilca', 'provincia': 'Huancayo', 'categoria': 'Cultural sites', 'corazon': {'contador': 0, 'marcado': False}}, {'image': 'imagen', 'nombre': 'Feria Ganadera De Cuasimodo', 'provincia': 'Huancayo', 'categoria': 'Acontecimientos y Eventos', 'corazon': {'contador': 0, 'marcado': False}}, {'image': 'imagen', 'nombre': 'Chongos Alto', 'provincia': 'Huancayo', 'categoria': 'Cultural sites', 'corazon': {'contador': 0, 'marcado': False}}, {'image': 'imagen', 'nombre': 'Cochas Chico', 'provincia': 'Huancayo', 'categoria': 'Cultural sites', 'corazon': {'contador': 0, 'marcado': False}}]
    recommendedResources = getRecommendedResources(None, 5)
    self.assertEqual(len(recommendedResources), 5)
    self.assertEqual(recommendedResources, respuestaEsperada)
    for i in recommendedResources:
      self.assertEqual(i["corazon"]["marcado"], False)

""" Testing del requerimieto RF06 () """
class FilterResource_TestCase(TestCase):
  fixtures = ["all.json"]
  
  def setUp(self):
    pass

  def test_userSocial_auth_getFilteredResources(self):
    userSocial = SocialAccount.objects.first()
    provincia = None
    distrito = None
    categoria = None
    self.client.force_login(userSocial.user)
    filteredResources = getFilteredResources(userSocial, provincia, distrito, categoria)
    print(filteredResources)



# get distritosJsobn