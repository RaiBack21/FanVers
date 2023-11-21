// під час завантаження сторінки
window.onload = function () {
    // спроба витягти збережений колір із localStorage
    var savedColor = localStorage.getItem('bgcolor');
    var savedSwitchState = localStorage.getItem('switchState');

    // якщо є збережений колір, застосувати його до тіла
    if (savedColor) {
        document.body.style.backgroundColor = savedColor;
    }

    // якщо є збережений стан перемикача, встановити його
    if (savedSwitchState) {
        document.getElementById(savedSwitchState).checked = true;
    }

    //додати обробники подій на радіо-кнопки
    document.getElementById('item2-state-off').addEventListener('change', changeBgColorAndSwitchState);
    document.getElementById('item2-state-null').addEventListener('change', changeBgColorAndSwitchState);
    document.getElementById('item2-state-on').addEventListener('change', changeBgColorAndSwitchState);
}

//функція для зміни кольору фону та збереження його вlocalStorage
function changeBgColorAndSwitchState(event) {
    var color;
    switch (event.target.id) {
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