const socket = io();

special_symbols = {
    S: '<i class="material-icons">brightness_low</i>',
    F: '<i class="material-icons">eco</i>',
    W: '<i class="material-icons">ac_unit</i>',
    P: '<i class="material-icons">local_florist</i>',
}


function main() {
    socket.on('connect', function () {
        socket.emit('register', {});
    });

    socket.on('state_changed', function state_changed(data) {
        document.getElementById(data.element).outerHTML = data.html;
        document.getElementById("overlay").style.display = data.show_overlay ? 'block' : 'none';
        makePretty();
    });

    socket.on('prompt_win', function state_changed(data) {
        document.getElementById("overlay").innerHTML = data.html;
        makePretty();
    });

    socket.on('game_won', function state_changed(data) {
        document.getElementById("overlay").innerHTML = data.html;
        makePretty();
    });
}

function select(self) {
    if (self.getAttribute('selected') == "False") {
        const tiles = document.querySelectorAll('.tile');
        Array.from(tiles).forEach((tile, index) => {
            tile.setAttribute('selected', tile == self ? 'True' : 'False');
        });
    } else {
        console.log(`${self.getAttribute('suit')}-${self.textContent}`)
        socket.emit('discard_tile', self.getAttribute('id'))
    }
}

function win(decision) {
    if (decision == 'accept') {
        socket.emit('accept_win')
    } else {
        document.getElementById("overlay").setAttribute('display', 'none')
    }
}


function steal(self) {
    socket.emit('steal_tile', self.parentElement.getAttribute('index'));
}


function makePretty() {
    console.log("Making pretty!");
    const tiles = document.querySelectorAll('.tile');
    console.log(`${tiles.length} tiles`);

    Array.from(tiles).forEach((tile, index) => {
        for (const [key, value] of Object.entries(special_symbols)) {
            if (tile.textContent == key) {
                tile.innerHTML = value
            }
        }
    });
}

$(document).ready(makePretty)
main()