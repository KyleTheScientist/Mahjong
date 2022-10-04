from uuid import uuid4
from flask import render_template
from flask_socketio import call
from resource import log, string_list, color
from gameplay.deck import Tile

def no_overlap(*lists):
    total_length = 0
    s = set()
    for i in lists:
        s = s.union([t.uuid for t in i])
        total_length += len(i)
    return len(s) == total_length

class Player:
    def __init__(self, name, socketio):
        self.name = name
        self.id = str(uuid4())
        self.discards = []
        self.hand = Hand()
        self.socketio = socketio
        self.can_play = False

    def deal(self, tile):
        for t in self.hand.hidden:
            t.selected = False
        self.hand.hidden.append(tile)
        tile.selected = True
        self.drawn_tile = tile
        
    def has_win(self):
        self.winning_hands = self.hand.winning_hands()
        if len(self.winning_hands) > 0:
            log(f"{self.name} has {len(self.winning_hands)} winning hands!")
            return True
        return False

    def update(self):
        self.hand.sort()
        if not self.can_play:
            self.drawn_tile = None
            for tile in self.hand.hidden:
                tile.selected = False
        for datatype in ['hand', 'steal_options', 'revealed_groups']:
            data = {
                'html': render_template(f"{datatype}.html", player=self), 
                'element': datatype,
                'can_play': self.can_play,
            }
            self.socketio.emit("state_changed", data, to=self.sessionID)
    
    def set_can_play(self, can_play):
        self.can_play = can_play
        self.update()

    def steal_options(self, tile):
        return self.hand.steal_options(tile)

    def prompt_steal(self, tile, steal_options):
        log(f"{self.name} has an opportunity to steal {tile}")
        self._steal_tile = tile
        self._steal_options = steal_options
        # tile.selected = True
        self.update()

    def prompt_win(self):
        self.socketio.emit('prompt_win', { 
            'html': render_template('win-prompt.html', player=self, winning_hand=self.winning_hands[0]),
        })

    def steal(self, group):
        log(f"{self.name}: Stealing group {group}")
        self.hand.hidden.append(self._steal_tile)
        tiles = self._steal_options[group]
        self.hand.reveal(tiles)
        self.update()

    def end_steal(self):
        self._steal_options = []
        self._steal_tile = None
        self.update()

    def discard(self, id):
        discarded = None
        self.drawn_tile = None
        for tile in self.hand.hidden:
            tile.selected = False
            if id == str(tile.id):
                discarded = tile
        if discarded:
            log(f"{self.name} is discarding {tile}")
            self.hand.hidden.remove(discarded)
            return discarded
        raise LookupError(f"Tile with id '{id}' not found in {self.name}'s hand.")

    def __getattr__(self, name):
        if name == 'hidden':
            return self.hand.hidden
        if name == 'revealed':
            return self.hand.hidden
        return self.__getattribute__(name)


class Hand:

    def __init__(self):
        self.hidden = []
        self.revealed = []

    def reveal(self, tiles):
        for tile in tiles:
            self.hidden.remove(tile)
        self.revealed.append(tiles)

    def sort(self):
        self.hidden.sort()

    def steal_options(self, tile):
        options = self.runs_with_tile(tile)
        triplet = self.triplets_with_tile(tile)
        if triplet:
            options.append(triplet)
        return options

    def winning_hands(self):
        if len(self.hidden + self.revealed) < 14: return []
        
        # Gather the components (groups) of a winning hand
        runs = self.runs_in_hand()
        triplets = self.triplets_in_hand()
        completed_groups = self.revealed.copy()
        
        ### Searching for a combination of 4 groups with no overlap
        default_search_space = runs + triplets + completed_groups
        if len(default_search_space) < 4: # If we don't have enough groups to form even one possible combination, we can move on.
            return []

        # If we have stolen some sets, they are stuck together permanently and must be used as-is, so we can reduce the search space
        # one of the stolen groups for as many as are available.
        search_spaces = [([completed_groups[i]] if i < len(completed_groups) else default_search_space) for i in range(4) ]
        potential_wins = []
        for group1 in search_spaces[0]:
            for group2 in search_spaces[1]:
                if no_overlap(group1, group2):
                    for group3 in search_spaces[2]:
                        if no_overlap(group1, group2, group3):
                            for group4 in search_spaces[3]:
                                if no_overlap(group1, group2, group3, group4):
                                    potential_win = [group1, group2, group3, group4]
                                    potential_win.sort()
                                    if not potential_win in potential_wins:
                                        potential_wins.append(potential_win)

        ### Searching for a pair
        # For each combination of 4 groups with no overlap, we check to see if, once all the tiles in the combination are removed,
        # there are two matching tiles left.
        winning_hands = []
        for potential_win in potential_wins:
            hand = self.all_tiles()
            for group in potential_win:
                for tile in group:
                    hand.remove(tile)
            a, b = hand
            if a.id == b.id:
                potential_win.append([a, b])
                winning_hands.append(potential_win)

        return winning_hands
    

    def runs_in_hand(self):
        digit_tiles = [t for t in self.hidden if (t.numeric())]
        return self.runs(digit_tiles)

    def triplets_in_hand(self):
        self.hidden.sort()
        triplets = []
        last = Tile('K9')
        for tile in self.hidden:
            if tile.id != last.id:
                triplet = []
            triplet.append(tile)
            if len(triplet) == 3:
                triplets.append(triplet)
                triplet = []
            last = tile
        return triplets
    
    def runs_with_tile(self, tile):
        if not tile.numeric():
            return []
        
        digit_tiles = [t for t in self.hidden if (t.numeric() and t.color == tile.color)]
        digit_tiles.append(tile)
        
        runs = []
        potential_runs = self.runs(digit_tiles)
        for potential_run in potential_runs: 
            potential_run.sort()
            if tile in potential_run and not potential_run in runs:
                runs.append(potential_run)
        return runs

    def triplets_with_tile(self, tile):
        matches = [tile]
        for t in self.hidden:
            if t.id == tile.id:
                matches.append(t)
        if len(matches) == 3:
            return matches
        return None
            
    def runs(self, tileset):
        # Basically brute forcing it with slight optimization
        potential_runs = []
        for a in tileset:
            first = a.number
            for b in tileset:
                second = b.number
                if second == first + 1 and a.color == b.color:
                    for c in tileset:
                        third = c.number
                        if third == second + 1 and b.color == c.color:
                            potential_runs.append([a, b, c])
        return potential_runs

    def all_tiles(self):
        tiles = [tile for tile in self.hidden]
        for group in self.revealed:
            tiles.extend(group)
        return tiles

