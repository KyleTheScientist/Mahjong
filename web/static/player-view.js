const socket = io();

import { makePretty } from './common.js';

function main() {
    socket.on('connect', function () {
        socket.emit('register', {});
    });

    socket.on('state_changed', function (updates) {
        Array.from(updates).forEach((data, index) => {
            document.getElementById(data.element).outerHTML = data.html;
        });
        makePretty();
    });
}

function select(self) {
    if (self.getAttribute('selected') == "False") {
        const tiles = document.querySelectorAll('.tile.hidden');
        console.log(tiles.length);
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

window.select = select;
window.win = win;
window.restart = restart;
window.steal = steal;


$(document).ready(makePretty)
main()