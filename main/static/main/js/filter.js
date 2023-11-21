// function ajaxSend(url, params) {
//   fetch(`${url}?${params}`, {
//     method: 'GET',
//     headers: {
//       'Content-Type': 'application/x-www-form-urlencoded',
//     },
//   })
//   .then(response => response.json())
//   .then(json => render(json))
//   .catch(error => console.error(error))
// }
//
//
// const forms = document.querySelector('form[name=filter]');
//
// forms.addEventListener('submit', function(e){
//   e.preventDefault();
//   let url = this.action;
//   let params = new URLSearchParams(new FormData(this)).toString();
//   ajaxSend(url, params);
// });
//
// function render(data) {
//   let template = Hogan.compile(html);
//   let output = template.render(data);
//
//   const div = document.querySelector('.cat_cards');
//   div.innerHTML = output;
// }
//
// let html = `\
// {{#books}}\
//   <div class="cat_card">\
//     <a href="{% url 'catalog:Book_Base' slug=book.slug %}">\
//       <img src="{{ image }}" alt="" />\
//     </a>\
//       <p class="catalog_title">{{ title }}</p>\
//       <div class="cat_card_desc">\
//         <div>\
//           <p>Статус:</p>\
//           <p>{{ status }}</p>\
//         </div>\
//         <div>\
//           <p>Фендом:</p>\
//           <p>{{ fandoms.name }}</p>\
//         </div>\
//     </div>\
//   </div>\
// {{/books}}`
//
//   // <script src="http://twitter.github.io/hogan.js/builds/3.0.1/hogan-3.0.1.js"></script>
