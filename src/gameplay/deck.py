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
        'M': 'magenta',
    }

    value = {
        '1': 1, '2': 2, '3': 3,
        '4': 4, '5': 5, '6': 6,
        '7': 7, '8': 8, '9': 9,
        'N': 1, 'E': 2, 'S': 3, 'W': 4, 'D': 5,
        'R': 1, 'G': 2, 'B': 3, 'Y': 4, 'M': 5
    }

    def __init__(self, id) -> None:
        self.symbol = id[1]
        self.color = id[0]
        self.suit = Tile.color_map[self.color]
        if self.numeric():
            self.id = Tile.value[id[0]] * 10 + Tile.value[id[1]]
            self.number = int(id[1])
        else:
            self.id = Tile.value[id[1]] * 100 + Tile.value[id[0]]
        self.uuid = uuid4()

    def numeric(self):
        return self.symbol.isdigit()

    def __str__(self):
        return f'[ {color(self.symbol, self.suit)} ]'

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


class Deck:
    def __init__(self):
        tiles = []
        for color in ['R', 'G', 'B']:
            for number in range(1, 10):
                for _ in range(4):
                    tiles.append(Tile(color + str(number)))

        for color in ['R', 'G', 'B']:
            for _ in range(4):
                tiles.append(Tile(color + 'D'))

        for direction in ['N', 'E', 'S', 'W']:
            for _ in range(4):
                tiles.append(Tile('M' + direction))

        tiles.sort()
        self.tiles = tiles
        
    def shuffle(self):
        shuffle(self.tiles)

    def draw(self):
        result = self.tiles[0]
        self.tiles = self.tiles[1:]
        return result