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
        <a class="flecha" href="/recurso-turistico/${nombre}/"><i class="fas fa-arrow-right"></i></a>
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

  let corazon = event.currentTarget;
  let corazon_count = corazon.parentNode.querySelector(".corazon__numero");
  fetch(`/api/update/favoritos?nombre=${nombre}`)
    .then(response => response.json())
    .then(data => {
      switch (data.message) {
        case "Se quito a favoritos":
          if(corazon.parentNode.classList.contains("corazon--active")){
            corazon.parentNode.classList.replace("corazon--active", "corazon--desactive")
            corazon_count.innerText = data.resource.corazones;
          }
          break;
        case "Se añadio a favoritos":
          if(corazon.parentNode.classList.contains("corazon--desactive")){
            corazon.parentNode.classList.replace("corazon--desactive", "corazon--active")
            corazon_count.innerText = data.resource.corazones;
          }
          break;
        case "Sin permisos":
          let modal = document.getElementById("modal-login");
          if(modal.classList.contains("modal--desactive"))
            modal.classList.replace("modal--desactive", "modal--active")
          break;
      }
      console.log(data);
      pedirCards && pedirCards();
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