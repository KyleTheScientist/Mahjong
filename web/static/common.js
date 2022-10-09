export const special_symbols = {
    S: '<span class="material-icons">brightness_low</span>',
    F: '<span class="material-icons">eco</span>',
    W: '<span class="material-icons">ac_unit</span>',
    P: '<span class="material-icons">local_florist</span>',
    
    I: '<span class="material-icons">local_fire_department</span>',
    T: '<span class="material-icons">water</span>',
    E: '<span class="material-icons">landscape</span>',
    A: '<span class="material-icons"></span>',
}

export function makePretty() {
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