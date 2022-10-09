const socket = io();

const special_symbols = {
    S: '<span class="material-icons">brightness_low</span>',
    F: '<span class="material-icons">eco</span>',
    W: '<span class="material-icons">ac_unit</span>',
    P: '<span class="material-icons">local_florist</span>',
    
    I: '<span class="material-icons">local_fire_department</span>',
    T: '<span class="material-icons">water</span>',
    E: '<span class="material-icons">landscape</span>',
    A: '<span class="material-icons"></span>',
}

function makePretty() {
    console.log("Making pretty!");
    const tiles = document.querySelectorAll('.tile');
    console.log(`${tiles.length} tiles`);

    Array.from(tiles).forEach((tile, index) => {
        console.log(tile.textContent.replace(/\s/g, ""));
        for (const [key, value] of Object.entries(special_symbols)) {
            if (tile.textContent.replace(/\s/g, "") == key) {
                tile.innerHTML = value
            }
        }
    });
}

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

    socket.on('hard_reset', function () {
        window.location.href = "/login";
    });
}

function select(self) {
    if (self.classList.contains("selected")) {
        console.log(`${self.getAttribute('suit')}-${self.textContent}`)
        socket.emit('discard_tile', self.getAttribute('id'))
    } else {
        const tiles = document.querySelectorAll('.tile.hidden');
        Array.from(tiles).forEach((tile, index) => {
            if (tile == self) {
                console.log(`Adding tag to ${tile.textContent}`);
                tile.classList.add('selected');
                tile.parentElement.classList.add('selected');
            } else {
                console.log(`Removing tag from ${tile.textContent}`);
                tile.classList.remove('selected');
                tile.parentElement.classList.remove('selected');
            }
        });
    }
}

function win(decision) {
    if (decision == 'accept') {
        socket.emit('win_response', 'True')
    } else {
        socket.emit('win_response', 'False')
    }
}

function scoreboard() {
    socket.emit('show_scoreboard')
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