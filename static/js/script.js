// Interpola los estilos de la barra de navegación, cuando el scroll es cero o mayor de cero
function activarAnimacionNavbar(){
  let navbar = document.querySelector('.fijo');
  window.onscroll = function() {
    if (window.pageYOffset > 0) {
      navbar.classList.add('fijo--scroll');
    } else {
      navbar.classList.remove('fijo--scroll');
    }
  }
}

// Agrega la interaccón a todos los menus desplegables
function activarAnimacionMenusDesplegables(){
  let selectionArray = document.querySelectorAll(".selection");

  selectionArray.forEach((selection) =>{
    let box = selection.querySelector(".selection__box");
    let optionList = selection.querySelector(".selection__option");
    let itemArray = selection.querySelectorAll(".selection__option__item");
    let content = selection.querySelector(".selection__box__content");
    let icon = selection.querySelector(".selection__box__icon");
    
    itemArray.forEach((item) => {
      item.addEventListener("click", (e) => {
        content.innerHTML = e.currentTarget.innerHTML;
        if(optionList.classList.contains("selection__option--open")){
          optionList.classList.replace("selection__option--open", "selection__option--close");
          icon.classList.replace("selection__box__icon--up", "selection__box__icon--down");
        }
        if(content.classList.contains("selection__box__content--void")){
          content.classList.replace("selection__box__content--void", "selection__box__content--full");
        }
      });
    });
    
    box.addEventListener("click", () => {
      if(optionList.classList.contains("selection__option--close") && !selection.classList.contains("selection--disabled")){
        optionList.classList.replace("selection__option--close", "selection__option--open");
        icon.classList.replace("selection__box__icon--down", "selection__box__icon--up");
      }
      else{
        optionList.classList.replace("selection__option--open", "selection__option--close");
        icon.classList.replace("selection__box__icon--up", "selection__box__icon--down");
      }
    });
  });

  window.addEventListener("click", (e) =>{
    const element = e.target;
    selectionArray.forEach((selection) =>{
      let optionList = selection.querySelector(".selection__option");
      let icon = selection.querySelector(".selection__box__icon");
      if(!selection.contains(element) && optionList.classList.contains("selection__option--open")){
        optionList.classList.replace("selection__option--open", "selection__option--close");
        icon.classList.replace("selection__box__icon--up", "selection__box__icon--down");
      }
    });
  });
}

// Coloca la lista de distritos correspondientes a una provincia dentro de las opciones del menu desplegable de distritos
function generarDistritos(provincia){
  let selection = document.getElementById("distritoSelection");
  let content = selection.querySelector(".selection__box__content");
  let optionList = selection.querySelector(".selection__option");
  let icon = selection.querySelector(".selection__box__icon");
  
  if(content != "Distrito" && document.getElementById("provincia").innerHTML != provincia){
    if(content.classList.contains("selection__box__content--full")){
      content.classList.replace("selection__box__content--full", "selection__box__content--void");
      content.innerHTML = "Distrito";
    }
  }
  selection.classList.remove("selection--disabled");
  fetch(`/api/distritos?provincia=${provincia}`)
  .then(response => response.json())
  .then(data => {
    let distritoArray = data;
    let distritosHTML = "";
    for (let i = 0; i < distritoArray.length; i++)
      distritosHTML += '<div class="selection__option__item">' + distritoArray[i] + '</div>'
    document.getElementById("distritoList").innerHTML = distritosHTML;

    let itemArray = document.getElementById("distritoList").querySelectorAll(".selection__option__item");
    itemArray.forEach((item) => {
      item.addEventListener("click", (e) => {
        content.innerHTML = e.currentTarget.innerHTML;
        if(optionList.classList.contains("selection__option--open")){
          optionList.classList.replace("selection__option--open", "selection__option--close");
          icon.classList.replace("selection__box__icon--up", "selection__box__icon--down");
        }
        if(content.classList.contains("selection__box__content--void")){
          content.classList.replace("selection__box__content--void", "selection__box__content--full");
        }
      });
    });
  });
}

// Devuelve en texto plano el HTML de una card
function generarCardHTML(imagen, nombre, provincia, categoria, corazones, marcado){
  let cardsHTML = `
    <div class="card">
      <div class="card__imagen">
        <img class="card__imagen__img" src="${imagen}" alt="${nombre}">
        <h5 class="card__imagen__titulo">${nombre}</h5>
        <p class="card__imagen__lugar">${provincia}</p>
      </div>
      <div class="card__descripcion">
        <div class="etiqueta">
          <span class="etiqueta__icono"><i class="fas fa-tag"></i></span>
          <span class="etiqueta__clase">${categoria}</span>
        </div>
        <div class="corazon ${(marcado) ? 'corazon--active' : 'corazon--desactive'}">
          <span class="corazon__icon" onclick="addFavoritos(event, '${nombre}')"><i class="fas fa-heart"></i><i class="far fa-heart"></i></span>
          <span class="corazon__numero">${corazones}</span>
        </div>
        <a class="flecha" href="/destinos/${nombre}/"><i class="fas fa-arrow-right"></i></a>
      </div>
    </div>
    `;
  return cardsHTML;
}

// Añade los botones para desplazarse en los recursos turisticos recomendados
function activarRecomendaciones(){
  let recomendadosArray =  document.querySelectorAll(".recomendados");
  recomendadosArray.forEach((recomendados) =>{
    let galeria = recomendados.querySelector(".recomendados__galeria");
    let btn_izq = recomendados.querySelector(".recomendados__button--izquierda");
    let btn_der = recomendados.querySelector(".recomendados__button--derecha");
    let card = recomendados.querySelector(".card");
    btn_izq && (btn_izq.style.display = (galeria.scrollLeft == 0)? "none": "flex");
    btn_der && (btn_der.style.display = (galeria.scrollWidth - galeria.scrollLeft == galeria.clientWidth) ? "none": "flex");
    
    galeria && galeria.addEventListener("scroll", () =>{
      btn_izq.style.display = (galeria.scrollLeft == 0)? "none": "flex";
      btn_der.style.display = (galeria.scrollWidth - galeria.scrollLeft == galeria.clientWidth) ? "none": "flex";
    });
  
    btn_der && btn_der.addEventListener("click",() => {
      galeria.scrollLeft += card.clientWidth + 30;
    });
    btn_izq && btn_izq.addEventListener("click",() => {
      galeria.scrollLeft += -card.clientWidth - 30;
    });
    
  });
}

// Agrega animacion a los checklist
function activarCheckList (){
  checklistArray = document.querySelectorAll(".checklist");
  (checklistArray.length > 0 ) && checklistArray.forEach((check) => {
    radioInput = check.querySelector(".checklist__input");
    radioInput.addEventListener('change', (e) =>{
      checklistArray.forEach((c) => {
        marca = c.querySelector(".checklist__marca");
        if(marca.classList.contains("checklist__marca--active")){
          marca.classList.replace("checklist__marca--active", "checklist__marca--desactive");
        }
      });
      marca = e.target.parentNode.querySelector(".checklist__marca");
      if(marca.classList.contains("checklist__marca--desactive")){
        marca.classList.replace("checklist__marca--desactive", "checklist__marca--active");
      }
    })
  });
}

// Activa el boton para cerrar el modal
function activarModal(){
  let modal = document.getElementById("modal-login");
  let button = document.getElementById("button-close");

  button.addEventListener("click", () => {
    if(modal.classList.contains("modal--active"))
      modal.classList.replace("modal--active", "modal--desactive")
  });
}

/* function activarCorazones(){
  let corazonesArray = document.querySelectorAll(".corazon--desactive");
  let modal = document.getElementById("modal-login");

  corazonesArray && corazonesArray.forEach(corazon => {
    let corazonbutton = corazon.querySelector(".corazon__icon")
    corazonbutton.addEventListener("click", () => {
      if(modal.classList.contains("modal--desactive"))
        modal.classList.replace("modal--desactive", "modal--active")
    });
  });
} */

function addFavoritos(event, nombre){
  const QUITAR = "QUITAR";
  const CAMBIAR_AÑADIR = "CAMBIAR_AÑADIR";
  const CREAR_AÑADIR = "CREAR_AÑADIR";
  const SIN_PERMISOS = "SIN_PERMISOS";

  let corazon = event.currentTarget;
  let corazon_count = corazon.parentNode.querySelector(".corazon__numero");
  fetch(`/api/add?nombre=${nombre}`)
    .then(response => response.json())
    .then(data => {
      switch (data.status) {
        case QUITAR:
          if(corazon.parentNode.classList.contains("corazon--active")){
            corazon.parentNode.classList.replace("corazon--active", "corazon--desactive")
            corazon_count.innerText = data.corazones;
          }
          break;
        case CAMBIAR_AÑADIR:
        case CREAR_AÑADIR:
          if(corazon.parentNode.classList.contains("corazon--desactive")){
            corazon.parentNode.classList.replace("corazon--desactive", "corazon--active")
            corazon_count.innerText = data.corazones;
          }
          break;
        case SIN_PERMISOS:
          let modal = document.getElementById("modal-login");
          if(modal.classList.contains("modal--desactive"))
            modal.classList.replace("modal--desactive", "modal--active")
          break;
        default:
          console.log("No es una opcion válida")
          break;
      }
      console.log(data.status)
      pedirCards && pedirCards()
    })
  /* if(corazon.parentNode.classList.contains("corazon--active")){
    corazon.parentNode.classList.replace("corazon--active", "corazon--desactive")
    corazon_count.innerText = parseInt(corazon_count.innerText) - 1;
  }
  else{
    corazon.parentNode.classList.replace("corazon--desactive", "corazon--active")
    corazon_count.innerText = parseInt(corazon_count.innerText) + 1;
  } */
}

function pedirRecomendaciones(resultado){
  fetch(`/api/recomendaciones?provincia=${provincia}&distrito=${distrito}&categoria=${categoria}`)
    .then(response => response.json())
    .then(data => {
      let cards = data;
      let cardsHTML = "";
      cards.forEach(({link, nombre, provincia, categoria, corazon}) => {
        cardsHTML += generarCardHTML(link, nombre, provincia, categoria, corazon.contador, corazon.marcado);
      });
      resultadoHTML = `
      <h4 class="recomendados__titulo">Recomendados para ti</h4>
      <div class="recomendados">
        <span class="recomendados__button--izquierda"><i class="fas fa-chevron-left"></i></span>
        <div class="recomendados__galeria">
          ${cardsHTML}
        </div>
        <span class="recomendados__button--derecha"><i class="fas fa-chevron-right"></i></span>
      </div>`;
      resultado.innerHTML = resultadoHTML;
      activarRecomendaciones();
    });
}