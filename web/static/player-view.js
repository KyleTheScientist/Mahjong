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

    socket.on('state_changed', function state_changed(updates) {
        Array.from(updates).forEach((data, index) => {
            document.getElementById(data.element).outerHTML = data.html;
        });
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
        socket.emit('win_response', 'True')
    } else {
        socket.emit('win_response', 'False')
    }
}

function restart() {
    socket.emit('restart')

}

function steal(choice) {
    if (choice == 'skip') {
        socket.emit('steal_tile', 'skip');
        return;
    }
    socket.emit('steal_tile', choice.parentElement.getAttribute('index'));
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