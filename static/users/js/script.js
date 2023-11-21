// $(document).ready(function() {
//   // Открыть модальное окно входа
//   $('#login-button').click(function() {
//     $('#login-modal').show();
//   });
//
//   // Закрыть модальное окно входа
//   $('#close-login').click(function() {
//     $('#login-modal').hide();
//   });
//
//   // Открыть модальное окно регистрации
//   $('#register-button').click(function() {
//     $('#register-modal').show();
//   });
//
//   // Закрыть модальное окно регистрации
//   $('#close-register').click(function() {
//     $('#register-modal').hide();
//   });
//
//   // Обработка формы входа
//   $('#login-form').submit(function(event) {
//     event.preventDefault();
//     $.ajax({
//       url: $(this).attr('action'),
//       type: 'POST',
//       data: $(this).serialize(),
//       success: function(response) {
//         // Обработка успешного входа
//       },
//       error: function(response) {
//         // Обработка ошибок входа
//       }
//     });
//   });
//
//   // Обработка формы регистрации
//   $('#signup-form').submit(function(event) {
//     event.preventDefault();
//     $.ajax({
//       url: $(this).attr('action'),
//       type: 'POST',
//       data: $(this).serialize(),
//       success: function(response) {
//         // Обработка успешной регистрации
//       },
//       error: function(response) {
//         // Обработка ошибок регистрации
//       }
//     });
//   });
// });
