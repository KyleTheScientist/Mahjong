function main() {
    const hand = document.getElementById('hand');
    var eventSource = new EventSource("/player_view")
    eventSource.onmessage = function (e) {
        targetContainer.innerHTML = e.data;
    //   hookButtons()
    };
}



main();