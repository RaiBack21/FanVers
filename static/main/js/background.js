  // при загрузке страницы
  window.onload = function() {
    // попытка извлечь сохранённый цвет из localStorage
    var savedColor = localStorage.getItem('bgcolor');
    var savedSwitchState = localStorage.getItem('switchState');

    // если есть сохранённый цвет, применить его к body
    if (savedColor) {
      document.body.style.backgroundColor = savedColor;
    }

    // если есть сохранённое состояние переключателя, установить его
    if (savedSwitchState) {
      document.getElementById(savedSwitchState).checked = true;
    }

    // добавить обработчики событий на радио-кнопки
    document.getElementById('item2-state-off').addEventListener('change', changeBgColorAndSwitchState);
    document.getElementById('item2-state-null').addEventListener('change', changeBgColorAndSwitchState);
    document.getElementById('item2-state-on').addEventListener('change', changeBgColorAndSwitchState);
  }

  // функция для изменения цвета фона и сохранения его в localStorage
  function changeBgColorAndSwitchState(event) {
    var color;
    switch(event.target.id) {
      case 'item2-state-off':
        color = '#1a1e29'; // включено
        break;
      case 'item2-state-null':
        color = '#ffe172'; // выключено
        break;
      case 'item2-state-on':
        color = '#fff'; // не задано
        break;
    }
    document.body.style.backgroundColor = color;
    localStorage.setItem('bgcolor', color);
    localStorage.setItem('switchState', event.target.id);
  }