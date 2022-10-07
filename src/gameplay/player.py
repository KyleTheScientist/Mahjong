from time import time
from uuid import uuid4
from flask import render_template
from flask_socketio import call
from resource import log, string_list, color
from gameplay.deck import Tile


def _no_overlap(*sets):
    # sets = [set(g) for g in groups]
    return len(frozenset.intersection(*sets)) == 0

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
        self.hand = Hand()
        self.socketio = socketio
        self.overlay = 'default'

    def reset(self):
        self.hand = Hand()
        self.overlay = 'default'
        self.update()

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

    def update(self, **kwargs):
        self.hand.sort()
        if self.overlay == 'default':
            self.drawn_tile = None
            for tile in self.hand.hidden:
                tile.selected = False
        data = []
        for datatype in ['hand', 'steal_options', 'revealed_groups', 'overlay']:
            data.append({
                'html': render_template(f"{datatype}.html", player=self, **kwargs), 
                'element': datatype,
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

        log(f"{self.name}: Stealing group {group}")
        self.hand.hidden.append(self._steal_tile)
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
        start_time = time()

        if len(self.all_tiles()) < 14: return []
        
        # Gather the components (groups) of a winning hand
        groups = self.revealed.copy()
        groups.extend(self.triplets_in_hand())
        groups.extend(self.runs_in_hand())

        ### Searching for a combination of 4 groups with no overlap
        potential_wins = []
        for groupA in groups:
            subsearchA = self.remove_tiles_from_groups(groupA, groups)
            for groupB in subsearchA:
                subsearchB = self.remove_tiles_from_groups(groupB, subsearchA)
                for groupC in subsearchB:
                    subsearchC = self.remove_tiles_from_groups(groupC, subsearchB)
                    for groupD in subsearchC:
                        potential_win = [groupA, groupB, groupC, groupD]
                        potential_win.sort()
                        if potential_win not in potential_wins:
                            potential_wins.append(potential_win)

        winning_hands = []
        for potential_win in potential_wins:
            hand = self.all_tiles()
            for group in potential_win:
                for tile in group:
                    hand.remove(tile)
            a, b = hand
            if a.id == b.id:
                potential_win.sort()
                potential_win.append([a, b])
                if potential_win not in winning_hands:
                    winning_hands.append(potential_win)

        log(f"Winning hand calculation took {int(time() - start_time)}s")
        return winning_hands
    
    def remove_tiles_from_groups(self, tiles, groups):
        result = []
        for group in groups:
            ok = True
            for t1 in group:
                for t2 in tiles:
                    if t1.uuid == t2.uuid:
                        ok = False
                        break
                    if not ok:
                        break
            if ok: result.append(group)
        return result

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

