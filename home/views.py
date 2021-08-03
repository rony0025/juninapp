import math
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count, Avg
from django.utils.translation import ugettext as _

from allauth.socialaccount.models import SocialAccount
from .models import Provincia, Categoria, Distrito, Recurso, Coordenada, Favorito, Comentario, Calificacion

""" Views para las páginas HTML """

def homeView(request):
  recommendedResources = []
  if request.user.is_authenticated:
    userSocial = SocialAccount.objects.get(user=request.user)
    recommendedResources = getRecommendedResources(userSocial, 10)
  else:
    recommendedResources = getRecommendedResources(None, 10)
  context ={
    "recomendados" : recommendedResources
  }
  context = contextAddUser(request, context)
  return render(request, 'pages/home.html', context)

def destinoView(request):
  provincias = Provincia.objects.all()
  categorias_tangibles = Categoria.objects.filter(tipo=True)
  recommendedResources = {}
  for categoria in categorias_tangibles:
    if request.user.is_authenticated:
      userSocial = SocialAccount.objects.get(user=request.user)
      recommendedResources[categoria.nombre] = getRecommendedResourcesCategory(userSocial, 3, categoria)
    else:
      recommendedResources[categoria.nombre] = getRecommendedResourcesCategory(None, 10, categoria)
  context ={
    "provincias": provincias,
    "categorias": categorias_tangibles,
    "recomendados" : recommendedResources
  }
  context = contextAddUser(request, context)
  return render(request, 'pages/destinos.html', context)

def culturaView(request):
  provincias = Provincia.objects.all()
  categorias_intangibles = Categoria.objects.filter(tipo=False)
  recommendedResources = {}
  for categoria in categorias_intangibles:
    if request.user.is_authenticated:
      userSocial = SocialAccount.objects.get(user=request.user)
      recommendedResources[categoria.nombre] = getRecommendedResourcesCategory(userSocial, 3, categoria)
    else:
      recommendedResources[categoria.nombre] = getRecommendedResourcesCategory(None, 10, categoria)
  context ={
    "provincias": provincias,
    "categorias": categorias_intangibles,
    "recomendados" : recommendedResources
  }
  context = contextAddUser(request, context)
  return render(request, 'pages/cultura.html', context)

def recursoTuristicoView(request, nombre):
  recursoQuery = Recurso.objects.filter(nombre=nombre)
  if(recursoQuery.exists()):
    recurso = recursoQuery.get()
    recursoTuristico = {
      "nombre": recurso.nombre,
      "imagen": recurso.image_URL,
      "provincia": recurso.distrito_id.provincia_id.nombre,
      "distrito": recurso.distrito_id.nombre,
      "categoria": recurso.categoria_id.nombre,
      "subtitulo": recurso.subtitulo,
      "descripcion": recurso.descripcion,
      "corazones": Favorito.objects.filter(recurso_id=recurso, is_active=True).count(),
      "marcado": False,
    }
    
    if request.user.is_authenticated:
      user = SocialAccount.objects.get(user=request.user)
      recursoTuristico["marcado"] = Favorito.objects.filter(recurso_id=recurso, usuario_id=user, is_active=True).exists()
    recommendedResources = []
    if request.user.is_authenticated:
      userSocial = SocialAccount.objects.get(user=request.user)
      recommendedResources = getRecommendedResourcesExclude(userSocial, 10, recurso.id)
    else:
      recommendedResources = getRecommendedResourcesExclude(None, 10, recurso.id)
    comentarios = []
    for comentario in Comentario.objects.order_by("-fecha")[:10]:
      comentarios.append({
        "usuario":{
          "nombre": comentario.usuario_id.extra_data["name"],
          "avatar": comentario.usuario_id.extra_data["picture"]
        },
        "fecha": comentario.fecha,
        "descripcion": comentario.descripcion
      })
    context = {
      "recurso": recursoTuristico,
      "recomendados" : recommendedResources,
      "comentarios": comentarios
    };
    context = contextAddUser(request, context)
    return render(request, 'pages/lugar.html', context)
  else:
    return render(request, 'no_econtrado.html')

def favoritosView(request):
  provincias = Provincia.objects.all()
  categorias_tangibles = Categoria.objects.filter(tipo=True)
  categorias_no_tangibles = Categoria.objects.filter(tipo=False)
  context ={
    "provincias": provincias,
    "categorias": {
      "tangibles": categorias_tangibles,
      "no_tangibles": categorias_no_tangibles
    }
  }
  if request.user.is_authenticated:
    context = contextAddUser(request, context)
    return render(request, 'pages/favoritos-auth.html', context)
  else:
    return render(request, 'pages/favoritos.html')

""" Views para los datos en """

def recommendationsJson(request):
  data = []
  if request.user.is_authenticated:
    userSocial = SocialAccount.objects.get(user=request.user)
    data = getRecommendedResources(userSocial, 10)
  else:
    data = getRecommendedResources(None, 10)
  return JsonResponse(data, safe=False)

def coordenadasJson(request):
  nombre = request.GET["nombre"];
  data = {
    "latitud": 0,
    "longuitud": 0,
  }
  if Coordenada.objects.filter(recurso_id__nombre=nombre).exists():
    coordenada = Coordenada.objects.filter(recurso_id__nombre=nombre).get()
    data["latitud"] = coordenada.latitud
    data["longuitud"] = coordenada.longitud
  return JsonResponse(data, safe=False)

def distritosJson(request):
  provinciaGET = request.GET['provincia']
  data=[]
  try:
    provinciaID = int(provinciaGET)
    provinciaQuery = Provincia.objects.filter(id=provinciaID)
    if provinciaQuery.exists():
      for distrito in Distrito.objects.filter(provincia_id__id=provinciaID):
        data.append({
          "id": distrito.id,
          "nombre": distrito.nombre
        })
  except:
    return JsonResponse([], safe=False)
  return JsonResponse(data, safe=False)

def filteredResourcesTangiblesJson(request):
  provinciaGET = request.GET["provincia"];
  distritoGET = request.GET["distrito"];
  categoriaGET = request.GET["categoria"];
  data = []
  try:
    provinciaID = int(provinciaGET)
    provinciaQuery = Provincia.objects.filter(id=provinciaID)
    if provinciaQuery.exists():
      provincia = provinciaQuery.get()
    else:
      provincia = None
  except:
    provincia = None
  try:
    distritoID = int(distritoGET)
    distritoQuery = Distrito.objects.filter(id=distritoID)
    if distritoQuery.exists():
      distrito = distritoQuery.get()
    else:
      distrito = None
  except:
    distrito = None
  try:
    categoriaID = int(categoriaGET)
    categoriaQuery = Categoria.objects.filter(id=categoriaID)
    if categoriaQuery.exists():
      categoria = categoriaQuery.get()
    else:
      categoria = None
  except:
    categoria = None

  if request.user.is_authenticated:
    userSocial = SocialAccount.objects.get(user=request.user)
    data = getFilteredResources(userSocial, provincia, distrito, categoria, True)
  else:
    data = getFilteredResources(None, provincia, distrito, categoria, True)
  return JsonResponse(data, safe=False)

def filteredResourcesIntangiblesJson(request):
  provinciaGET = request.GET["provincia"];
  distritoGET = request.GET["distrito"];
  categoriaGET = request.GET["categoria"];
  data = []
  try:
    provinciaID = int(provinciaGET)
    provinciaQuery = Provincia.objects.filter(id=provinciaID)
    if provinciaQuery.exists():
      provincia = provinciaQuery.get()
    else:
      provincia = None
  except:
    provincia = None
  try:
    distritoID = int(distritoGET)
    distritoQuery = Distrito.objects.filter(id=distritoID)
    if distritoQuery.exists():
      distrito = distritoQuery.get()
    else:
      distrito = None
  except:
    distrito = None
  try:
    categoriaID = int(categoriaGET)
    categoriaQuery = Categoria.objects.filter(id=categoriaID)
    if categoriaQuery.exists():
      categoria = categoriaQuery.get()
    else:
      categoria = None
  except:
    categoria = None
  if request.user.is_authenticated:
    userSocial = SocialAccount.objects.get(user=request.user)
    data = getFilteredResources(userSocial, provincia, distrito, categoria, False)
  else:
    data = getFilteredResources(None, provincia, distrito, categoria, False)
  return JsonResponse(data, safe=False)

def getFavoritos(request):
  provinciaGET = request.GET["provincia"];
  distritoGET = request.GET["distrito"];
  categoriaGET = request.GET["categoria"];
  data = []
  try:
    provinciaID = int(provinciaGET)
    provinciaQuery = Provincia.objects.filter(id=provinciaID)
    if provinciaQuery.exists():
      provincia = provinciaQuery.get()
    else:
      provincia = None
  except:
    provincia = None
  try:
    distritoID = int(distritoGET)
    distritoQuery = Distrito.objects.filter(id=distritoID)
    if distritoQuery.exists():
      distrito = distritoQuery.get()
    else:
      distrito = None
  except:
    distrito = None
  try:
    categoriaID = int(categoriaGET)
    categoriaQuery = Categoria.objects.filter(id=categoriaID)
    if categoriaQuery.exists():
      categoria = categoriaQuery.get()
    else:
      categoria = None
  except:
    categoria = None

  if request.user.is_authenticated:
    userSocial = SocialAccount.objects.get(user=request.user)
    data = getFavoriteFilteredResources(userSocial, provincia, distrito, categoria)
  return JsonResponse(data, safe=False)

def updateFavoritos(request):
  nombreGET = request.GET["nombre"];
  data = {}
  recursoQuery = Recurso.objects.filter(nombre=nombreGET)
  if not request.user.is_authenticated:
    return JsonResponse({"message" : "Sin permisos"}, safe=False)
  elif not recursoQuery.exists():
    return JsonResponse({"message" : "No exite el recurso"}, safe=False)
  else:
    userSocial = SocialAccount.objects.get(user=request.user)
    resource = recursoQuery.get()
    response = updateFavoriteResources(userSocial, resource)
    if response["is_favorite"]:
      data = {"message" : "Se añadio a favoritos", "resource": response["resource"]}
    else:
      data = {"message" : "Se quito a favoritos", "resource": response["resource"]}
  return JsonResponse(data, safe=False)

def getComentarios(request):
  nombreGET = request.GET["nombre"];
  paginaGET = request.GET["pagina"];
  
  user = None
  user_logeado = None
  if request.user.is_authenticated:
    user = SocialAccount.objects.get(user=request.user)
  recursoQuery = Recurso.objects.filter(nombre=nombreGET)
  if recursoQuery.exists():
    recurso = recursoQuery.get()
  else:
    return JsonResponse({"message": "No existe el recurso"}, safe=False)
  try:
    pagina = int(paginaGET)
  except ValueError:
    return JsonResponse({"message": "La pagina no es un numero"}, safe=False)
  except:
    return JsonResponse({"message": "Ocurrio un error no esperado"}, safe=False)
  cant_comentarios = Comentario.objects.filter(recurso_id=recurso).count()
  if cant_comentarios == 0:
    return JsonResponse({
      "cant_comentarios": 0,
      "comentarios": [],
      "siguiente_pagina": None
    }, safe=False)

  cant_paginas = math.ceil(cant_comentarios / 10)
  if not (1 <= pagina and pagina <= cant_paginas):
    return JsonResponse({"message": "Pagina invalida"}, safe=False)
  comentarios = []
  if cant_comentarios != 0:
    for comentario in Comentario.objects.filter(recurso_id=recurso).order_by("-fecha")[(pagina - 1) * 10: pagina * 10]:
      comentarios.append({
        "id": comentario.id,
        "editable": comentario.usuario_id == user,
        "usuario":{
          "nombre": comentario.usuario_id.extra_data["name"],
          "avatar": comentario.usuario_id.extra_data["picture"]
        },
        "fecha": comentario.fecha.strftime('%Y %b, %d %H:%M %p'),
        "descripcion": comentario.descripcion
      })
  if cant_paginas < pagina + 1:
    siguiente_pagina = None
  else:
    siguiente_pagina = pagina + 1
  return JsonResponse({
    "cant_comentarios": cant_comentarios,
    "comentarios": comentarios,
    "siguiente_pagina": siguiente_pagina
  }, safe=False)

def addComentario(request):
  nombreGET = request.GET["nombre"];
  comentarioGET = request.GET["comentario"];
  data = {}
  if request.user.is_authenticated:
    user = SocialAccount.objects.get(user=request.user)
  else:
    return JsonResponse({
      "error": {
        "ID": 1,
        "message": "No tiene los permisos"
      }
    }, safe=False)
  recursoQuery = Recurso.objects.filter(nombre=nombreGET)
  if recursoQuery.exists():
    recurso = recursoQuery.get()
  else:
    return JsonResponse({
      "error": {
        "ID": 2,
        "message": "No existe el recurso"
      }
    }, safe=False)
  if comentarioGET == "":
    return JsonResponse({
      "error": {
        "ID": 3,
        "message": "El comentario no puede estar vacio"
      }
    }, safe=False)
  else:
    Comentario.objects.create(usuario_id=user, recurso_id=recurso, descripcion=comentarioGET)
    return JsonResponse({
      "successful": {
        "ID": 1,
        "message": "Se añadio el comentario"
      }
    }, safe=False)
  return JsonResponse(data, safe=False)

def deleteComentario(request):
  idComentarioGET = request.GET["id"];
  data = {}
  if request.user.is_authenticated:
    user = SocialAccount.objects.get(user=request.user)
  else:
    return JsonResponse({
      "error": {
        "ID": 1,
        "message": "No tiene los permisos"
      }
    }, safe=False)
  try:
    idComentario = int(idComentarioGET)
  except ValueError:
    return JsonResponse({
      "error": {
        "ID": 4,
        "message": "El id no es un numero"
      }
    }, safe=False)
  except:
    return JsonResponse({
      "error": {
        "ID": 5,
        "message": "Ocurrio un error no esperado"
      }
    }, safe=False)
  comentarioQuery = Comentario.objects.filter(id=idComentario)
  if not comentarioQuery.exists():
    return JsonResponse({
      "error": {
        "ID": 2,
        "message": "No existe el comentario"
      }
    }, safe=False)
  else:
    if not comentarioQuery.filter(usuario_id=user).exists():
      return JsonResponse({
        "error": {
          "ID": 3,
          "message": "El comentario no es de su propiedad"
        }
      }, safe=False)
    else:
      comentarioQuery.delete()
      return JsonResponse({
        "successful": {
          "ID": 1,
          "message": "Se elimino el comentario"
        }
      }, safe=False)
  return JsonResponse(data, safe=False)

def getCalificacion(request):
  nombreGET = request.GET["nombre"];
  data = {
    "opiniones": 0,
    "calificacion": {
      "Accesibilidad": 0,
      "Aforo": 0,
      "EcoAmigable": 0,
      "Educativo": 0,
      "Recreacional": 0
    },
    "mi_calificacion": {
      "Accesibilidad": 0,
      "Aforo": 0,
      "EcoAmigable": 0,
      "Educativo": 0,
      "Recreacional": 0
    }
  }    
  recursoQuery = Recurso.objects.filter(nombre=nombreGET)
  if recursoQuery.exists():
    recurso = recursoQuery.annotate(
      accesibilidadScore=Avg('calificacion__accesibilidad'),
      aforoScore=Avg('calificacion__aforo'),
      eco_amigableScore=Avg('calificacion__eco_amigable'),
      educativoScore=Avg('calificacion__educativo'),
      recreacionalScore=Avg('calificacion__recreacional'),
      cant_opiniones=Count('calificacion')
    ).get()
    data = {
      "opiniones": recurso.cant_opiniones,
      "calificacion": {
        "Accesibilidad": recurso.accesibilidadScore,
        "Aforo": recurso.aforoScore,
        "EcoAmigable": recurso.eco_amigableScore,
        "Educativo": recurso.educativoScore,
        "Recreacional": recurso.recreacionalScore
      },
      "mi_calificacion": {
        "Accesibilidad": 0,
        "Aforo": 0,
        "EcoAmigable": 0,
        "Educativo": 0,
        "Recreacional": 0
      }
    }
    if request.user.is_authenticated:
      user = SocialAccount.objects.get(user=request.user)
      mi_calificacionQuery = Calificacion.objects.filter(recurso_id__nombre=nombreGET, usuario_id=user)
      if mi_calificacionQuery.exists():
        mi_calificacion = mi_calificacionQuery.get()
        data["mi_calificacion"] = {
          "Accesibilidad": mi_calificacion.accesibilidad,
          "Aforo": mi_calificacion.aforo,
          "EcoAmigable": mi_calificacion.eco_amigable,
          "Educativo": mi_calificacion.educativo,
          "Recreacional": mi_calificacion.recreacional
        }
  return JsonResponse(data, safe=False)

def updateCalificacion(request):
  nombreGET = request.GET["nombre"];
  accesibilidadGET = request.GET["accesibilidad"];
  aforoGET = request.GET["aforo"];
  eco_amigableGET = request.GET["eco_amigable"];
  educativoGET = request.GET["educativo"];
  recreacionalGET = request.GET["recreacional"];

  recursoQuery = Recurso.objects.filter(nombre=nombreGET)
  if not request.user.is_authenticated:
    return JsonResponse({"message" : "Sin permisos"}, safe=False)
  elif not recursoQuery.exists():
    return JsonResponse({"message" : "No exite el recurso"}, safe=False)
  else:
    try:
      accesibilidad_score = int(accesibilidadGET)
      aforo_score = int(aforoGET)
      eco_amigable_score = int(eco_amigableGET)
      educativo_score = int(educativoGET)
      recreacional_score = int(recreacionalGET)
    except:
      return JsonResponse({"message": "Un puntaje no es un entero"}, safe=False)
    if not ((0 <= accesibilidad_score and accesibilidad_score <= 5) and (0 <= aforo_score and aforo_score <= 5) and (0 <= eco_amigable_score and eco_amigable_score <= 5) and (0 <= educativo_score and educativo_score <= 5) and (0 <= recreacional_score and recreacional_score <= 5)):
      return JsonResponse({"message": "Un puntaje en esta fuera del rango permitido"}, safe=False)
    else:
      recurso = recursoQuery.get()
      userSocial = SocialAccount.objects.get(user=request.user)
      calificacionQuery = Calificacion.objects.filter(recurso_id=recurso, usuario_id=userSocial)
      if calificacionQuery.exists():
        calificacionQuery.update(accesibilidad=accesibilidad_score, aforo=aforo_score, eco_amigable=eco_amigable_score, educativo=educativo_score, recreacional=recreacional_score)
        recurso.puntuacion = calcularPuntuacionRecurso(recurso)
        recurso.save()
        return JsonResponse({"message": "Se actualizo la calificacion"}, safe=False)
      else:
        Calificacion.objects.create(accesibilidad=accesibilidad_score, aforo=aforo_score, eco_amigable=eco_amigable_score, educativo=educativo_score, recreacional=recreacional_score, usuario_id=userSocial, recurso_id=recurso)
        return JsonResponse({"message": "Se añadio la calificacion"}, safe=False)

""" Funciones """

def calcularPuntuacionRecurso(resource):
  puntuacion = 0
  recurso = Recurso.objects.filter(id=resource.id).annotate(
    accesibilidad=Avg('calificacion__accesibilidad'),
    aforo=Avg('calificacion__aforo'),
    eco_amigable=Avg('calificacion__eco_amigable'),
    educativo=Avg('calificacion__educativo'),
    recreacional=Avg('calificacion__recreacional')
  ).get()
  accesibilidad = recurso.accesibilidad
  if accesibilidad == None:
    accesibilidad = 0
  aforo = recurso.aforo
  if aforo == None:
    aforo = 0
  eco_amigable = recurso.eco_amigable
  if eco_amigable == None:
    eco_amigable = 0
  educativo = recurso.educativo
  if educativo == None:
    educativo = 0
  recreacional = recurso.recreacional
  if recreacional == None:
    recreacional = 0
  promedio_calificacion = (accesibilidad + aforo + eco_amigable + educativo + recreacional) / 5
  cant_corazones = Favorito.objects.filter(recurso_id=resource, is_active=True).count()
  puntuacion = int(cant_corazones + promedio_calificacion * 100)
  return puntuacion

def getFavoriteFilteredResources(userSocial, provincia, distrito, categoria):
  favoriteResources = []
  if userSocial != None:
    recursosQuery = Recurso.objects.filter(favoritos__usuario_id=userSocial, favoritos__is_active=True).order_by('-puntuacion')
    if provincia != None:
      recursosQuery = recursosQuery & Recurso.objects.filter(distrito_id__provincia_id=provincia)
    if distrito != None:
      recursosQuery = recursosQuery & Recurso.objects.filter(distrito_id=distrito)
    if categoria != None:
      recursosQuery = recursosQuery & Recurso.objects.filter(categoria_id=categoria)
    for recurso in recursosQuery:
      imagen = recurso.image_URL
      nombre = recurso.nombre
      provincia = recurso.distrito_id.provincia_id.nombre
      distrito = recurso.distrito_id.nombre
      categoria = recurso.categoria_id.nombre
      corazones = Favorito.objects.filter(recurso_id=recurso, is_active=True).count()
      marcado = True
      card = crearCardRecurso(imagen, nombre, provincia, categoria, corazones, marcado)
      favoriteResources.append(card)
  return favoriteResources

def getFilteredResources(userSocial, provincia, distrito, categoria, is_tangibles):
  filteredResources = []
  recursosQuery = Recurso.objects.filter(categoria_id__tipo=is_tangibles).order_by('-puntuacion')
  if provincia != None:
    recursosQuery = recursosQuery & Recurso.objects.filter(distrito_id__provincia_id=provincia)
  if distrito != None:
    recursosQuery = recursosQuery & Recurso.objects.filter(distrito_id=distrito)
  if categoria != None:
    recursosQuery = recursosQuery & Recurso.objects.filter(categoria_id=categoria)
  for recurso in recursosQuery:
    imagen = recurso.image_URL
    nombre = recurso.nombre
    provincia = recurso.distrito_id.provincia_id.nombre
    distrito = recurso.distrito_id.nombre
    categoria = recurso.categoria_id.nombre
    corazones = Favorito.objects.filter(recurso_id=recurso, is_active=True).count()
    if userSocial != None:
      marcado = Favorito.objects.filter(recurso_id=recurso, usuario_id=userSocial, is_active=True).exists()
    else:
      marcado = False
    card = crearCardRecurso(imagen, nombre, provincia, categoria, corazones, marcado)
    filteredResources.append(card)
  return filteredResources

def updateFavoriteResources(userSocial, resource):
  is_favorite = False
  favoritoQuery = Favorito.objects.filter(usuario_id=userSocial, recurso_id=resource)
  if favoritoQuery.exists():
    if favoritoQuery.filter(is_active=True).exists():
      resourceChange = favoritoQuery.update(is_active=False)
      is_favorite = False
    else:
      resourceChange = favoritoQuery.update(is_active=True)
      is_favorite = True
  else:
    resourceChange = Favorito.objects.create(usuario_id=userSocial, recurso_id=resource, is_active=True)
    is_favorite = True
    newScore = calcularPuntuacionRecurso(resource)
    resource.puntuacion = newScore
    resource.save()
  response = {
    "resource": {
      "id": resource.id,
      "nombre": resource.nombre,
      "corazones": Favorito.objects.filter(recurso_id=resource, is_active=True).count()
    },
    "is_favorite": is_favorite
  }
  return response

def getRecommendedResources(userSocial, quantity):
  recommendedResources = []
  if quantity > 0:
    for recurso in Recurso.objects.order_by('-puntuacion')[:quantity]:
      imagen = recurso.image_URL
      nombre = recurso.nombre
      provincia = recurso.distrito_id.provincia_id.nombre
      categoria = recurso.categoria_id.nombre
      corazones = Favorito.objects.filter(recurso_id=recurso, is_active=True).count()
      if userSocial != None:
        marcado = Favorito.objects.filter(recurso_id=recurso, usuario_id=userSocial, is_active=True).exists()
      else:
        marcado = False
      card = crearCardRecurso(imagen, nombre, provincia, categoria, corazones, marcado)
      recommendedResources.append(card)
  return recommendedResources

def getRecommendedResourcesExclude(userSocial, quantity, resourceID):
  recommendedResources = []
  if quantity > 0:
    for recurso in Recurso.objects.order_by('-puntuacion').exclude(id=resourceID)[:quantity]:
      imagen = recurso.image_URL
      nombre = recurso.nombre
      provincia = recurso.distrito_id.provincia_id.nombre
      categoria = recurso.categoria_id.nombre
      corazones = Favorito.objects.filter(recurso_id=recurso, is_active=True).count()
      if userSocial != None:
        marcado = Favorito.objects.filter(recurso_id=recurso, usuario_id=userSocial, is_active=True).exists()
      else:
        marcado = False
      card = crearCardRecurso(imagen, nombre, provincia, categoria, corazones, marcado)
      recommendedResources.append(card)
  return recommendedResources

def getRecommendedResourcesCategory(userSocial, quantity, category):
  recommendedResources = []
  if quantity > 0:
    for recurso in Recurso.objects.filter(categoria_id=category).order_by('-puntuacion')[:quantity]:
      imagen = recurso.image_URL
      nombre = recurso.nombre
      provincia = recurso.distrito_id.provincia_id.nombre
      categoria = recurso.categoria_id.nombre
      corazones = Favorito.objects.filter(recurso_id=recurso, is_active=True).count()
      if userSocial != None:
        marcado = Favorito.objects.filter(recurso_id=recurso, usuario_id=userSocial, is_active=True).exists()
      else:
        marcado = False
      card = crearCardRecurso(imagen, nombre, provincia, categoria, corazones, marcado)
      recommendedResources.append(card)
  return recommendedResources

def crearCardRecurso(imagen, nombre, provincia, categoria, corazones, marcado):
  recursoCard = {
    'image': imagen,
    'nombre': nombre,
    'provincia': provincia,
    'categoria': categoria,
    'corazon': {
      "contador": corazones,
      "marcado": marcado
    }
  }
  return recursoCard

def contextAddUser(request, context):
  user = {
    "is_authenticated": request.user.is_authenticated
  }
  if request.user.is_authenticated:
    data = SocialAccount.objects.get(user=request.user).extra_data
    user["nombre"] = data["name"]
    user["imagen"] = data["picture"]

  context["user"] = user
  return context
