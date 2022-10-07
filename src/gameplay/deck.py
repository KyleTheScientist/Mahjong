from random import shuffle
from colorama import init, Fore, Style
from uuid import uuid4
from resource import color

class Tile:
    color_map = {
        'R': 'red',
        'G': 'green',
        'B': 'blue',
        'Y': 'yellow',
        'O': 'orange',
        'C': 'cyan',
        'M': 'magenta',
        'K': 'black',
    }

    value = {
        # Digits
        '1': 1, '2': 2, '3': 3,
        '4': 4, '5': 5, '6': 6,
        '7': 7, '8': 8, '9': 9,
        # Seasons
        'S': 1, 'F': 2, 'W': 3, 'P': 4,
        # Elements
        'I': 5, 'E': 7, 'T': 6, 'A': 8,
        # Colors
        'R': 1, 'G': 2, 'B': 3, 'Y': 4, 'O': 5, 'C': 6, 'M': 7, 'K': 8,
    }

    uuid_counter = 0

    def __init__(self, id) -> None:
        self.symbol = id[1]
        self.color = id[0]
        self.suit = Tile.color_map[self.color]
        if self.numeric():
            self.id = Tile.value[id[0]] * 10 + Tile.value[id[1]]
            self.number = int(id[1])
        else:
            self.id = Tile.value[id[1]] * 100 + Tile.value[id[0]]
        self.uuid = Tile.uuid_counter
        Tile.uuid_counter += 1


    def numeric(self):
        return self.symbol.isdigit()

    def __str__(self):
        clr = 'yellow' if self.suit == 'orange' else self.suit
        return f'[ {color(self.symbol, clr)} ]'

    def __lt__(self, other):
        return self.id < other.id

    def __le__(self, other):
        return self.id <= other.id

    def __eq__(self, other):
        if not type(other) is Tile: return False
        return self.id == other.id

    def __ne__(self, other):
        return self.id != other.id

    def __gt__(self, other):
        return self.id > other.id

    def __ge__(self, other):
        return self.id >= other.id

    def __hash__(self) -> int:
        return self.uuid


class Deck:
    def __init__(self):
        tiles = []
        for color in ['R', 'G', 'B']:
            for number in range(1, 10):
                for _ in range(4):
                    tiles.append(Tile(color + str(number)))

        for element, color in [('I', 'R'), ('T', 'B'), ('E', 'G'), ('A', 'K')]:
            for _ in range(4):
                tiles.append(Tile(color + element))

        for season, color in [('S', 'K'), ('F', 'K'), ('W', 'K'), ('P', 'K')]:
            for _ in range(4):
                tiles.append(Tile(color + season))

        tiles.sort()
        self.tiles = tiles
        
    def shuffle(self):
        shuffle(self.tiles)

    def draw(self):
        result = self.tiles[0]
        self.tiles = self.tiles[1:]
        return result