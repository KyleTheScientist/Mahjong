const socket = io();

function main() {
    socket.on('player_joined', function state_changed(data) {
        document.getElementById('player-counter').textContent = data.html;
    });
    socket.on('start_game', function state_changed(data) {
        console.log("Party leader started the game");
        window.location.href = "/game/player_view";
    });
}

function startGame() {
    console.log("Starting game");
    socket.emit('request_start_game')
}

main();