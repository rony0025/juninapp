import math
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count, Avg

from allauth.socialaccount.models import SocialAccount
from .models import Provincia, Categoria, Distrito, Recurso, Coordenada, Favorito, Comentario, Calificacion

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

# Envía los recursos turístico recomendados que se mostrará en la página principal
def homeView(request):
  recomendados = []
  if request.user.is_authenticated:
    user = SocialAccount.objects.get(user=request.user)
    for recurso in Recurso.objects.order_by('-puntuacion')[:8]:
      imagen = recurso.image_URL
      nombre = recurso.nombre
      provincia = recurso.distrito_id.provincia_id.nombre
      categoria = recurso.categoria_id.nombre
      corazones = Favorito.objects.filter(recurso_id=recurso, is_active=True).count()
      marcado = Favorito.objects.filter(recurso_id=recurso, usuario_id=user, is_active=True).exists()
      recomendados.append(crearCardRecurso(imagen, nombre, provincia, categoria, corazones, marcado))
  else:
    for recurso in Recurso.objects.order_by('-puntuacion')[:8]:
      imagen = recurso.image_URL
      nombre = recurso.nombre
      provincia = recurso.distrito_id.provincia_id.nombre
      categoria = recurso.categoria_id.nombre
      corazones = Favorito.objects.filter(recurso_id=recurso, is_active=True).count()
      marcado = False
      recomendados.append(crearCardRecurso(imagen, nombre, provincia, categoria, corazones, marcado))

  context ={
    "recomendados" : recomendados
  }
  context = contextAddUser(request, context)
  return render(request, 'pages/home.html', context)

# Envía los lugares turístico recomendados por categoría (naturales, culturales, realizaciones), las provincias de Junín y las categorías (Sitios Naturales, Sitios Culturales, Realizaciones Contemporáneas) que se mostrará en la página de destinos
def destinoView(request):
  provincias = Provincia.objects.all()
  categoriasTangibles = Categoria.objects.filter(tipo=True)
  recomendados = {}
  if request.user.is_authenticated:
    user = SocialAccount.objects.get(user=request.user)
    for categoria in categoriasTangibles:
      categoriaNombre = categoria.nombre
      recomendados[categoriaNombre] = []
      for recurso in Recurso.objects.filter(categoria_id=categoria).order_by("-puntuacion")[:3]:
        imagen = recurso.image_URL
        nombre = recurso.nombre
        provincia = recurso.distrito_id.provincia_id.nombre
        categoria = recurso.categoria_id.nombre
        corazones = Favorito.objects.filter(recurso_id=recurso, is_active=True).count()
        marcado = Favorito.objects.filter(recurso_id=recurso, usuario_id=user, is_active=True).exists()
        recomendados[categoriaNombre].append(crearCardRecurso(imagen, nombre, provincia, categoria, corazones, marcado))
  else:
    for categoria in categoriasTangibles:
      categoriaNombre = categoria.nombre
      recomendados[categoriaNombre] = []
      for recurso in Recurso.objects.filter(categoria_id=categoria).order_by("-puntuacion")[:3]:
        imagen = recurso.image_URL
        nombre = recurso.nombre
        provincia = recurso.distrito_id.provincia_id.nombre
        categoria = recurso.categoria_id.nombre
        corazones = Favorito.objects.filter(recurso_id=recurso, is_active=True).count()
        marcado = False
        recomendados[categoriaNombre].append(crearCardRecurso(imagen, nombre, provincia, categoria, corazones, marcado))
  context ={
    "provincias": provincias,
    "categorias": categoriasTangibles,
    "recomendados" : recomendados
  }
  context = contextAddUser(request, context)
  return render(request, 'pages/destinos.html', context)

# Envía los datos del lugar turístico que pidió el cliente desde su navegador y los recursos turísticos recomendados que se mostrará en la página respectiva al lugar turístico pedido.
def lugarTuristicoView(request, nombre):
  if(Recurso.objects.filter(nombre=nombre).exists()):
    recursoTuristico = {}
    recomendados = []
    recurso = Recurso.objects.filter(nombre=nombre).get()
    recursoTuristico["nombre"] = recurso.nombre
    recursoTuristico["imagen"] = recurso.image_URL
    recursoTuristico["provincia"] = recurso.distrito_id.provincia_id.nombre
    recursoTuristico["distrito"] = recurso.distrito_id.nombre
    recursoTuristico["categoria"] = recurso.categoria_id.nombre
    recursoTuristico["subtitulo"] = recurso.subtitulo
    recursoTuristico["descripcion"] = recurso.descripcion
    recursoTuristico["corazones"] = Favorito.objects.filter(recurso_id=recurso, is_active=True).count()
    recursoTuristico["marcado"] = False
    if request.user.is_authenticated:
      user = SocialAccount.objects.get(user=request.user)
      recursoTuristico["marcado"] = Favorito.objects.filter(recurso_id=recurso, usuario_id=user, is_active=True).exists()
      for recurso in Recurso.objects.order_by('-puntuacion').exclude(nombre=nombre)[:8]:
        imagen = recurso.image_URL
        nombre_recurso = recurso.nombre
        provincia = recurso.distrito_id.provincia_id.nombre
        categoria = recurso.categoria_id.nombre
        corazones = Favorito.objects.filter(recurso_id=recurso, is_active=True).count()
        marcado = Favorito.objects.filter(recurso_id=recurso, usuario_id=user, is_active=True).exists()
        recomendados.append(crearCardRecurso(imagen, nombre_recurso, provincia, categoria, corazones, marcado))
    else:
      for recurso in Recurso.objects.order_by('-puntuacion').exclude(nombre=nombre)[:8]:
        imagen = recurso.image_URL
        nombre_recurso = recurso.nombre
        provincia = recurso.distrito_id.provincia_id.nombre
        categoria = recurso.categoria_id.nombre
        corazones = Favorito.objects.filter(recurso_id=recurso, is_active=True).count()
        marcado = False
        recomendados.append(crearCardRecurso(imagen, nombre_recurso, provincia, categoria, corazones, marcado))
    calificacion = {
      "criterio_1": 1,
      "criterio_2": 3,
      "criterio_3": 4,
    }
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
      "recomendados" : recomendados,
      "calificacion": calificacion,
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

# Envía un archivo json con los distritos correspondientes de provincia (donde la provincia es pasada como un parámetro de una petición GET)
def getDistritos(request):
  provincia = request.GET['provincia']
  data=[]
  if Provincia.objects.filter(nombre=provincia).exists():
    for distrito in Distrito.objects.filter(provincia_id__nombre=provincia):
      data.append(distrito.nombre)
  return JsonResponse(data, safe=False)

# Envía un archivo json con los lugares turísticos correspondientes al filtro que realizó el cliente desde su navegador (donde los parámetros del filtro por provincia, por distrito y por categoría son pasados como parámetros de una petición GET)
def getDestinos(request):
  provinciaGET = request.GET["provincia"];
  distritoGET = request.GET["distrito"];
  categoriaGET = request.GET["categoria"];
  data = []
  if request.user.is_authenticated:
    user = SocialAccount.objects.get(user=request.user)
    for recurso in Recurso.objects.order_by('nombre'):
      imagen = recurso.image_URL
      nombre = recurso.nombre
      provincia = recurso.distrito_id.provincia_id.nombre
      distrito = recurso.distrito_id.nombre
      categoria = recurso.categoria_id.nombre
      corazones = Favorito.objects.filter(recurso_id=recurso, is_active=True).count()
      marcado = Favorito.objects.filter(recurso_id=recurso, usuario_id=user, is_active=True).exists()
      card = crearCardRecurso(imagen, nombre, provincia, categoria, corazones, marcado)
      card["distrito"] = recurso.distrito_id.nombre
      data.append(card)
  else:
    for recurso in Recurso.objects.order_by('-puntuacion'):
      imagen = recurso.image_URL
      nombre = recurso.nombre
      provincia = recurso.distrito_id.provincia_id.nombre
      categoria = recurso.categoria_id.nombre
      corazones = Favorito.objects.filter(recurso_id=recurso, is_active=True).count()
      marcado = False
      card = crearCardRecurso(imagen, nombre, provincia, categoria, corazones, marcado)
      card["distrito"] = recurso.distrito_id.nombre
      data.append(card)

  if Provincia.objects.filter(nombre=provinciaGET).exists():
    newData = []
    for r in data:
      if r["provincia"] == provinciaGET:
        newData.append(r)
    data = newData
  if Distrito.objects.filter(nombre=distritoGET).exists():
    newData = []
    for r in data:
      if r["distrito"] == distritoGET:
        newData.append(r)
    data = newData
  if Categoria.objects.filter(nombre=categoriaGET).exists():
    newData = []
    for r in data:
      if r["categoria"] == categoriaGET:
        newData.append(r)
    data = newData
  return JsonResponse(data, safe=False)

# Envía un archivo json con las coordenada de un lugar turístico (donde el nombre del lugar turístico es pasado como parámetro de una petición GET)
def getCoordenadas(request):
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

# Envía un archivo json con las coordenada de un lugar turístico (donde el nombre del lugar turístico es pasado como parámetro de una petición GET)
def getRecomendaciones(request):
  data = []
  if request.user.is_authenticated:
    user = SocialAccount.objects.get(user=request.user)
    for recurso in Recurso.objects.order_by('-puntuacion')[:8]:
      imagen = recurso.image_URL
      nombre = recurso.nombre
      provincia = recurso.distrito_id.provincia_id.nombre
      categoria = recurso.categoria_id.nombre
      corazones = Favorito.objects.filter(recurso_id=recurso, is_active=True).count()
      marcado = Favorito.objects.filter(recurso_id=recurso, usuario_id=user, is_active=True).exists()
      data.append(crearCardRecurso(imagen, nombre, provincia, categoria, corazones, marcado))
  else:
    for recurso in Recurso.objects.order_by('-puntuacion')[:8]:
      imagen = recurso.image_URL
      nombre = recurso.nombre
      provincia = recurso.distrito_id.provincia_id.nombre
      categoria = recurso.categoria_id.nombre
      corazones = Favorito.objects.filter(recurso_id=recurso, is_active=True).count()
      marcado = False
      data.append(crearCardRecurso(imagen, nombre, provincia, categoria, corazones, marcado))
  return JsonResponse(data, safe=False)

def getRecursos(request):
  provincia = request.GET["provincia"];
  distrito = request.GET["distrito"];
  categoria = request.GET["categoria"];
  recursosFavoritos = []
  if request.user.is_authenticated:
    user = SocialAccount.objects.get(user=request.user)
    favoritos = Favorito.objects.order_by("-recurso_id__puntuacion").filter(usuario_id=user, is_active=True)
    for favorito in favoritos:
      recurso = favorito.recurso_id        
      imagen = recurso.image_URL
      nombre = recurso.nombre
      provinciaNombre = recurso.distrito_id.provincia_id.nombre
      categoriaNombre = recurso.categoria_id.nombre
      corazones = Favorito.objects.filter(recurso_id=recurso, is_active=True).count()
      marcado = True
      card = crearCardRecurso(imagen, nombre, provinciaNombre, categoriaNombre, corazones, marcado)
      card["distrito"] = recurso.distrito_id.nombre
      recursosFavoritos.append(card)
    if Provincia.objects.filter(nombre=provincia).exists():
      newData = []
      for r in recursosFavoritos:
        if r["provincia"] == provincia:
          newData.append(r)
      recursosFavoritos = newData
    if Distrito.objects.filter(nombre=distrito).exists():
      newData = []
      for r in recursosFavoritos:
        if r["distrito"] == distrito:
          newData.append(r)
      recursosFavoritos = newData
    if Categoria.objects.filter(nombre=categoria).exists():
      newData = []
      for r in recursosFavoritos:
        if r["categoria"] == categoria:
          newData.append(r)
      recursosFavoritos = newData
  return JsonResponse(recursosFavoritos, safe=False)

def addFavoritos(request):
  nombre = request.GET["nombre"];
  data = {}
  if request.user.is_authenticated and Recurso.objects.filter(nombre=nombre).exists():
    recurso = Recurso.objects.get(nombre=nombre)
    user = SocialAccount.objects.get(user=request.user)
    if Favorito.objects.filter(usuario_id=user, recurso_id=recurso).exists():
      favorito = Favorito.objects.get(usuario_id=user, recurso_id=recurso)
      if favorito.is_active == True:
        favorito.is_active = False
        favorito.save()
        data["status"] = "QUITAR"
      else:
        favorito.is_active = True
        favorito.save()
        data["status"] = "CAMBIAR_AÑADIR"
    else:
      Favorito.objects.create(usuario_id=user, recurso_id=recurso, is_active=True)
      data["status"] = "CREAR_AÑADIR"
    cant_corazones = Favorito.objects.filter(recurso_id=recurso, is_active=True).count()
    recurso.puntuacion = calcularPuntuacionRecurso(recurso.id)
    recurso.save()
    data["corazones"] = cant_corazones
  else:
    data["status"] = "SIN_PERMISOS"
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
    return JsonResponse({
      "error": {
        "ID": 1,
        "message": "No existe el recurso"
      }
    }, safe=False)
  try:
    pagina = int(paginaGET)
  except ValueError:
    return JsonResponse({
      "error": {
        "ID": 2,
        "message": "La pagina no es un numero"
      }
    }, safe=False)
  except:
    return JsonResponse({
      "error": {
        "ID": 3,
        "message": "Ocurrio un error no esperado"
      }
    }, safe=False)
  cant_comentarios = Comentario.objects.filter(recurso_id=recurso).count()
  if cant_comentarios == 0:
    return JsonResponse({
      "cant_comentarios": 0,
      "comentarios": [],
      "siguiente_pagina": None
    }, safe=False)

  cant_paginas = math.ceil(cant_comentarios / 10)
  if not (1 <= pagina and pagina <= cant_paginas):
    return JsonResponse({
      "error": {
        "ID": 4,
        "message": "Pagina invalida"
      }
    }, safe=False)
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

def borrarComentario(request):
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
      accesibilidad=Avg('calificacion__criterio1'),
      aforo=Avg('calificacion__criterio2'),
      eco_amigable=Avg('calificacion__criterio3'),
      educativo=Avg('calificacion__criterio4'),
      recreacional=Avg('calificacion__criterio5'),
      cant_opiniones=Count('calificacion')
    ).get()
    data = {
      "opiniones": recurso.cant_opiniones,
      "calificacion": {
        "Accesibilidad": recurso.accesibilidad,
        "Aforo": recurso.aforo,
        "EcoAmigable": recurso.eco_amigable,
        "Educativo": recurso.educativo,
        "Recreacional": recurso.recreacional
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
          "Accesibilidad": mi_calificacion.criterio1,
          "Aforo": mi_calificacion.criterio2,
          "EcoAmigable": mi_calificacion.criterio3,
          "Educativo": mi_calificacion.criterio4,
          "Recreacional": mi_calificacion.criterio5
        }
  return JsonResponse(data, safe=False)

def updateCalificacion(request):
  nombreGET = request.GET["nombre"];
  accesibilidadGET = request.GET["accesibilidad"];
  aforoGET = request.GET["aforo"];
  eco_amigableGET = request.GET["eco_amigable"];
  educativoGET = request.GET["educativo"];
  recreacionalGET = request.GET["recreacional"];

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
  try:
    accesibilidad_score = int(accesibilidadGET)
    aforo_score = int(aforoGET)
    eco_amigable_score = int(eco_amigableGET)
    educativo_score = int(educativoGET)
    recreacional_score = int(recreacionalGET)
  except ValueError:
    return JsonResponse({
      "error": {
        "ID": 8,
        "message": "El puntaje no es un numero"
      }
    }, safe=False)
  except:
    return JsonResponse({
      "error": {
        "ID": 9,
        "message": "Ocurrio un error no esperado"
      }
    }, safe=False)
  if not (0 <= accesibilidad_score and accesibilidad_score <= 5):
    return JsonResponse({
      "error": {
        "ID": 3,
        "message": "El puntaje en 'Accesibilidad' esta fuera del rango permitido"
      }
    }, safe=False)
  if not (0 <= aforo_score and aforo_score <= 5):
    return JsonResponse({
      "error": {
        "ID": 4,
        "message": "El puntaje en 'Aforo' esta fuera del rango permitido"
      }
    }, safe=False)
  if not (0 <= eco_amigable_score and eco_amigable_score <= 5):
    return JsonResponse({
      "error": {
        "ID": 5,
        "message": "El puntaje en 'Eco amigable' esta fuera del rango permitido"
      }
    }, safe=False)
  if not (0 <= educativo_score and educativo_score <= 5):
    return JsonResponse({
      "error": {
        "ID": 6,
        "message": "El puntaje en 'Educativo' esta fuera del rango permitido"
      }
    }, safe=False)
  if not (0 <= recreacional_score and recreacional_score <= 5):
    return JsonResponse({
      "error": {
        "ID": 7,
        "message": "El puntaje en 'Recreacional' esta fuera del rango permitido"
      }
    }, safe=False)
  calificacionQuery = Calificacion.objects.filter(recurso_id=recurso, usuario_id=user)
  if calificacionQuery.exists():
    calificacionQuery.update(criterio1=accesibilidad_score, criterio2=aforo_score, criterio3=eco_amigable_score, criterio4=educativo_score, criterio5=recreacional_score)
    recurso.puntuacion = calcularPuntuacionRecurso(recurso.id)
    recurso.save()
    return JsonResponse({
      "successful": {
        "ID": 1,
        "message": "Se actualizo la calificacion"
      }
    }, safe=False)
  else:
    Calificacion.objects.create(recurso_id=recurso, usuario_id=user ,criterio1=accesibilidad_score, criterio2=aforo_score, criterio3=eco_amigable_score, criterio4=educativo_score, criterio5=recreacional_score)
    recurso.puntuacion = calcularPuntuacionRecurso(recurso.id)
    recurso.save()
    return JsonResponse({
      "successful": {
        "ID": 2,
        "message": "Se añadio la calificacion"
      }
    }, safe=False)
  return JsonResponse(data, safe=False)

def calcularPuntuacionRecurso(id_recurso):
  puntuacion = 0
  if Recurso.objects.filter(id=id_recurso).exists():
    recurso = Recurso.objects.filter(id=id_recurso).annotate(
      accesibilidad=Avg('calificacion__criterio1'),
      aforo=Avg('calificacion__criterio2'),
      eco_amigable=Avg('calificacion__criterio3'),
      educativo=Avg('calificacion__criterio4'),
      recreacional=Avg('calificacion__criterio5')
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
    cant_corazones = Favorito.objects.filter(recurso_id=recurso, is_active=True).count()
    puntuacion = int(cant_corazones + promedio_calificacion * 100)
    print(puntuacion)
  return puntuacion