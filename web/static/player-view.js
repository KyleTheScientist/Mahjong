const socket = io();

function main() {
    socket.on('connect', function () {
        socket.emit('register', {});
    });

    socket.on('state_changed', function state_changed(data) {
        document.getElementById(data.element).outerHTML = data.html;
        console.log(data.element);
        console.log(data.html);
        socket.emit('state_changed', { data: 'Success' });
    });
}

function select(self) {
    if (self.getAttribute('selected') == "False") {
        const elements = document.querySelectorAll('.tile');
        Array.from(elements).forEach((element, index) => {
            element.setAttribute('selected', element == self ? 'True' : 'False');
        });
    } else {
        console.log(`${self.getAttribute('suit')}-${self.textContent}`)
        socket.emit('discard_tile', self.getAttribute('id'))
    }
}


function steal(self) {
    socket.emit('steal_tile', self.parentElement.getAttribute('index'));
}


main();