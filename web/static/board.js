const socket = io();

special_symbols = {
    S: '<span class="material-icons">brightness_low</span>',
    F: '<span class="material-icons">eco</span>',
    W: '<span class="material-icons">ac_unit</span>',
    P: '<span class="material-icons">local_florist</span>',
    
    I: '<span class="material-icons">local_fire_department</span>',
    T: '<span class="material-icons">water</span>',
    E: '<span class="material-icons">landscape</span>',
    A: '<span class="material-icons"></span>',
}

socket.on('board_state_changed', function (updates) {
    Array.from(updates).forEach((data, index) => {
        console.log(`Updating ${data.element}`);
        document.getElementById(data.element).outerHTML = data.html;
    });
    makePretty();
});

function makePretty() {
    const tiles = document.querySelectorAll('.tile');

    Array.from(tiles).forEach((tile, index) => {
        for (const [key, value] of Object.entries(special_symbols)) {
            if (tile.textContent == key) {
                tile.innerHTML = value
            }
        }
    });
}

$(document).ready(makePretty)