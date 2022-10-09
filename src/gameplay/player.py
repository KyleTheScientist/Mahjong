from resource import color, log, string_list
from uuid import uuid4

from flask import render_template
from flask_socketio import call

from gameplay.hand import Hand

class Player:
    def __init__(self, name, game):
        self.name = name
        self.id = str(uuid4())
        self.game = game
        self.socketio = game.socketio
        self.score = 0
        self.reset()
    
    def reset(self, new_game=False):
        self.hand = Hand()
        self.discards = []
        self.overlay = 'default'
        self.winner = None
        if new_game: 
            self.score = 0

    def deal(self, tile):
        for t in self.hand.hidden:
            t.selected = False
        self.hand.hidden.append(tile)
        tile.selected = True
        tile.parent = self
        self.drawn_tile = tile
        
    def has_win(self):
        self.winning_hand = self.hand.winning_hand()
        if self.winning_hand:
            log(f"{self.name} has a winning hand!")
            return True
        return False

    def update(self, **kwargs):
        self.hand.sort()
        if self.overlay == 'default':
            self.drawn_tile = None
            for tile in self.hand.hidden:
                tile.selected = False
        data = []
        for datatype in ['hand', 'steal_options', 'revealed_groups', 'player-overlays']:
            data.append({
                'html': render_template(f"{datatype}.html", player=self, winner=self.game.winner, **kwargs), 
                'element': datatype if 'overlay' not in datatype else 'overlay',
            })
        self.socketio.emit("state_changed", data, to=self.sessionID)
    
    def set_overlay(self, overlay, **kwargs):
        self.overlay = overlay
        log(f"{self.name} set overlay to {overlay}")
        self.update(**kwargs)

    def steal_options(self, tile):
        return self.hand.steal_options(tile)

    def prompt_steal(self, tile, steal_options):
        log(f"{self.name} has an opportunity to steal {tile}")
        self._steal_tile = tile
        self._steal_options = steal_options
        # tile.selected = True
        self.update()

    def prompt_win(self):
        self.set_overlay('win-prompt')
        self.update()

    def steal(self, group):
        if group == 'skip':
            log(f"{self.name} declined to steal")
            return False

        stolen_tile = self._steal_tile
        log(f"{self.name}: Stealing group {group}")
        self.hand.hidden.append(stolen_tile)
        stolen_tile.parent.discards.remove(stolen_tile)
        stolen_tile.parent = self
        tiles = self._steal_options[int(group)]
        self.hand.reveal(tiles)
        self.update()
        return True

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
            self.discards.append(discarded)
            return discarded
        raise LookupError(f"Tile with id '{id}' not found in {self.name}'s hand.")

    def __getattr__(self, name):
        if name == 'hidden':
            return self.hand.hidden
        if name == 'revealed':
            return self.hand.hidden
        return self.__getattribute__(name)


