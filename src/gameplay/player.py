from uuid import uuid4
from flask import render_template
from flask_socketio import call
from resource import log

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
        options = self.potential_runs(tile)
        triplet = self.potential_triplet(tile)
        if triplet:
            options.append(triplet)
        return options
    
    def potential_runs(self, tile):
        if not tile.numeric():
            return []
        digit_tiles = [t for t in self.hidden if (t.numeric() and t.color == tile.color)]
        digit_tiles.append(tile)
        potential_runs = []
        
        # Basically brute forcing it with slight optimization
        for a in digit_tiles:
            first = a.number
            for b in digit_tiles:
                second = b.number
                if second == first + 1:
                    for c in digit_tiles:
                        third = c.number
                        if third == second + 1:
                            potential_runs.append([a, b, c])
            
        runs = []
        for potential_run in potential_runs: 
            potential_run.sort()
            if tile in potential_run and not potential_run in runs:
                runs.append(potential_run)
        return runs
            
    def potential_triplet(self, tile):
        matches = [tile]
        for t in self.hidden:
            if t.id == tile.id:
                matches.append(t)
        if len(matches) == 3:
            return matches
        return None
