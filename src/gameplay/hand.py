from collections import namedtuple
from resource import log
from time import time

from gameplay.deck import Tile


class Hand:
    modifiers = {
        'Winning Hand': 2,
        'No Stealing': 1,
        'Only One Suit': 1,
        'Large Straight': 1,
        'Same Group In All Suits': 1,
        'All Triplets': 2,
        'All Natural': 5,
    }

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

    def score(self, winning_hand): 
        modifiers = []
        self.add_modifier('Winning Hand', modifiers)
        points = 1
        if len(self.revealed) == 0:
            value = self.add_modifier('No Stealing', modifiers)
            points += value
        if self.only_one_suit():
            value = self.add_modifier('Only One Suit', modifiers)
            points += value
        if self.large_straight(winning_hand):
            value = self.add_modifier('Large Straight', modifiers)
            points += value
        if self.same_group_in_all_suits(winning_hand):
            value = self.add_modifier('Same Group In All Suits', modifiers)
            points += value
        if len(self.runs_in_hand()) == 0:
            value = self.add_modifier('All Triplets', modifiers)
            points += value
        if self.all_natural():
            value = self.add_modifier('All Natural', modifiers)
            points += value
        return points, modifiers
            
    def add_modifier(self, name, modifiers):
        modifiers.append({name: Hand.modifiers[name]})
        return Hand.modifiers[name]

    def all_natural(self):
        for tile in self.all_tiles():
            if tile.numeric(): return False
        return True

    def same_group_in_all_suits(self, hand):
        for group in hand:
            colors = { 'R': False, 'G': False, 'B': False}
            if not group[0].color in ["R", "G", "B"]:
                continue
            to_match = [t.symbol for t in group]
            for group2 in hand:
                if not group2[0].color in ["R", "G", "B"]:
                    continue
                if [t.symbol for t in group2] == to_match:
                    colors[group2[0].color] = True
            if colors['R'] and colors['G'] and colors['B']:
                return True
        return False

    def large_straight(self, hand):
        expected_number = 1
        expected_color = 'red'
        for group in hand[:-1]:
            a, b, c = group
            if not a.numeric() or b.number != a.number + 1: # Check if this is a run
                continue
            color = group[0].color
            if a.number != expected_number or color != expected_color:
                expected_number = 1
                if a.number == 1:
                    expected_number += 3
                    expected_color = a.color
                continue
            else:
                expected_number += 3
                if expected_number > 9:
                    return True
        return False

    def only_one_suit(self):
        tiles = self.all_tiles()
        color = tiles[0].color
        for tile in tiles:
            if tile.color != color:
                return False
        return True

    def winning_hand(self):
        WinningHand = namedtuple('WinningHand', 'hand,score,modifiers')
        hands = self.winning_hands()
        if len(hands) == 0:
            return None
        best_hand = hands[0]
        best_score, best_modifiers = self.score(hands[0])
        for hand in hands[1:]:
            score, modifiers = self.score(hand)
            if score > best_score:
                best_hand, best_score, best_modifiers = hand, score, modifiers
        return WinningHand(hand=best_hand, score=best_score, modifiers=best_modifiers)

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
