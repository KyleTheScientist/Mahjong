from random import shuffle
from colorama import init, Fore, Style
from uuid import uuid4
from os import get_terminal_size

def string_list(tiles):
    return ''.join([str(t) for t in tiles])

def no_overlap(*lists):
    total_length = 0
    s = set()
    for i in lists:
        s = s.union([t.uuid for t in i])
        total_length += len(i)
    return len(s) == total_length

def color(string, color):
    fore = getattr(Fore, color.upper())
    return f'{fore}{string}{Style.RESET_ALL}'

class Tile:
    color_map = {
        'R': 'RED',
        'G': 'GREEN',
        'B': 'BLUE',
        'Y': 'YELLOW',
        'M': 'MAGENTA',
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
        self.clr = id[0]
        self.color = Tile.color_map[self.clr]
        if self.numeric():
            self.id = Tile.value[id[0]] * 10 + Tile.value[id[1]]
            self.number = int(id[1])
        else:
            self.id = Tile.value[id[1]] * 100 + Tile.value[id[0]]
        self.uuid = uuid4()

    def numeric(self):
        return self.symbol.isdigit()

    def __str__(self):
        return f'[ {color(self.symbol, self.color)} ]'

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

        for color in ['R', 'G', 'B', 'Y']:
            for _ in range(4):
                tiles.append(Tile(color + 'D'))

        for direction in ['N', 'E', 'S', 'W']:
            for _ in range(4):
                tiles.append(Tile('M' + direction))

        tiles.sort()
        self.tiles = tiles
        
        print(string_list(self.tiles))

    def shuffle(self):
        shuffle(self.tiles)

    def draw(self):
        result = self.tiles[0]
        self.tiles = self.tiles[1:]
        return result


class Player:
    def __init__(self, name, index):
        self.name = name
        self.index = index
        self.hand = []
        self.revealed = []
        self.hidden = []
        self.discards = []

    def deal(self, input):
        if type(input) == Tile:
            self.hand.append(input)
            self.hidden.append(input)
        else:
            self.hand.extend(input)
            self.hidden.extend(input)
        self.sort_hand()

    def triplets(self):
        self.sort_hand()
        triplets = []

        last = Tile('R99')
        triplet = []
        for tile in self.hand:
            if tile.id != last.id:
                triplet = []
            triplet.append(tile)
            if len(triplet) == 3:
                triplets.append(triplet)
                triplet = []
            last = tile

        return triplets

    def runs(self):
        self.sort_hand()
        
        digit_tiles = [t for t in self.hand if t.numeric()]
        runs = []
        for a in digit_tiles:
            first = a.number
            for b in digit_tiles:
                second = b.number
                if second == first + 1 and b.clr == a.clr:
                    for c in digit_tiles:
                        third = c.number
                        if third == second + 1 and c.clr == b.clr:
                            runs.append([a, b, c])
        return runs

    def winning_hands(self):
        winning_hands = []
        runs = self.runs()
        triplets = self.triplets()
        groups = runs + triplets

        # TODO Force revealed tiles to remain in their group

        potential_wins = []
        # Basically brute forcing it with slight optimization
        for group1 in groups:
            for group2 in groups:
                if no_overlap(group1, group2):
                    for group3 in groups:
                        if no_overlap(group1, group2, group3):
                            for group4 in groups:
                                if no_overlap(group1, group2, group3, group4):
                                    potential_win = [group1, group2, group3, group4]
                                    potential_win.sort()
                                    if not potential_win in potential_wins:
                                        potential_wins.append(potential_win)
        
        for potential_win in potential_wins:
            hand = self.hand.copy()
            for group in potential_win:
                for tile in group:
                    hand.remove(tile)
            a, b = hand
            if a.id == b.id:
                potential_win.append([a, b])
                winning_hands.append(potential_win)
        return winning_hands

    def stealportunities(self, tile):
        # Check for triplets
        triplet = self.possible_triplet(tile)

        # If the tile is not a digit it cannot be a part of a run
        if not tile.numeric():
            if triplet:
                return [triplet]
            return []
        
        # Check for runs
        runs = self.possible_runs(tile)
        if triplet:
            runs.append(triplet)
        return runs
    
    def possible_runs(self, tile):
        digit_tiles = [t for t in self.hidden if t.numeric()]
        digit_tiles.append(tile)
        potential_runs = []
        
        # Basically brute forcing it with slight optimization
        for a in digit_tiles:
            first = a.number
            for b in digit_tiles:
                second = b.number
                if second == first + 1 and b.clr == a.clr:
                    for c in digit_tiles:
                        third = c.number
                        if third == second + 1 and c.clr == b.clr:
                            potential_runs.append([a, b, c])
            
        runs = []
        for potential_run in potential_runs: 
            potential_run.sort()
            if tile in potential_run and not potential_run in runs:
                runs.append(potential_run)
        return runs
            
    def possible_triplet(self, tile):
        matches = [tile]
        for t in self.hidden:
            if t.id == tile.id:
                matches.append(t)
        if len(matches) == 3:
            return matches
        return None
        
    def discard(self, tile):
        self.discards.append(tile)
        self.hidden.remove(tile)
        self.hand.remove(tile)
        self.sort_hand()

    def sort_hand(self):
        self.hand.sort()
        self.hidden.sort()

    def __str__(self):
        discards = string_list(self.discards)
        hidden = string_list(self.hidden)
        revealed = string_list(self.revealed)
        result = f'''{self.name}\n{discards}\n{"-" * 14 * 5}\n{hidden}        {revealed}'''.strip()
        return result


class Game:
    hand_size = 14

    def __init__(self) -> None:
        self.deck = Deck()
        self.players = []
        self.player_count = 0
        self.turn = 0

    def add_player(self, name):
        self.players.append(Player(name, self.player_count))
        self.player_count += 1

    def start(self):
        shuffle(self.players)
        for i, player in enumerate(self.players):
            player.index = i
        self.deal()
        while True:
            player = self.players[self.turn]
            tile = self.deck.draw()
            player.deal(tile)
            
            hands = player.winning_hands()
            if len(hands) > 0:
                print('Winning hand(s) available!')
                for hand in hands:
                    print('---'.join([string_list(t) for t in hand]))
                exit()

            self.prompt_discard(player, highlight=tile) 

    def check_for_steals(self, tile):
        turn = self.turn
        for i in range(self.player_count - 1):
            player = self.players[(turn + i + 1) % self.player_count]
            stealportunities = player.stealportunities(tile) 
            if len(stealportunities) > 1:
                 if self.prompt_steal(player, tile, stealportunities):
                    return True
        return False
    
    def prompt_steal(self, player, tile, stealportunities):
        prompt = f"Steal {tile}?    (0) Don't Steal | "
        for i, group in enumerate(stealportunities):
            prompt += f'({i + 1}) {string_list(group)} | '

        while True:
            # print(player.name)
            print('~' * get_terminal_size().columns)
            print("Your hand:", string_list(player.hand))
            print(prompt)
            choice = input("Choose a group to complete: ")
            if choice.isdigit() and 0 <= int(choice) <= len(stealportunities):
                break
        
        choice = int(choice)
        if choice == 0: return False
        player.deal(tile)
        for tile in stealportunities[choice - 1]:
            player.revealed.append(tile)
            player.hidden.remove(tile)
        self.prompt_discard(player)

    
    def prompt_discard(self, player, highlight=None):
        print("Prompting", self.turn, player.index)
        self.turn = player.index
        while True:
            print('~' * get_terminal_size().columns)
            print(str(player))
            indices = ''.join([str(i).center(5) for i in range(1, len(player.hidden) + 1)])
            if highlight:
                index = player.hidden.index(highlight) + 1
                indices = indices.replace(f' {index} ', f' {color(index, "yellow")} ')
            print(indices)
            choice = input("Choose a tile to discard: ")
            if choice.isdigit() and 0 < int(choice) <= len(player.hidden):
                break

        choice = int(choice) - 1
        if self.check_for_steals(player.hidden[choice]): return
        player.discard(player.hidden[choice])
        # print(player.name, player.index, self.player_count,  (player.index + 1) % self.player_count)
        self.turn = (player.index + 1) % self.player_count


    def deal(self):
        self.deck.shuffle()
        for _ in range(Game.hand_size - 1):
            for player in self.players:
                player.deal(self.deck.draw())


if __name__ == "__main__":
    init()
    game = Game()
    game.add_player("Kyle")
    game.add_player("Hannah")
    game.start()
