import sys
from time import time
import unittest
import colorama
from unittest.mock import Mock, MagicMock

# sys.modules['resource'] = MagicMock()
# sys.modules['gameplay.deck'] = __import__('deck')

from gameplay.deck import Tile
from gameplay.player import Player, Hand, no_overlap
from resource import string_list

colorama.init()

def triplets(tiles):
    return hand_function('triplets', tiles)

def runs(tiles):
    return hand_function('runs', tiles)

def winning_hands(tiles):
    return hand_function('winning_hands', tiles)

def hand_function(func, tiles):
    player = Player("Test", 0)
    player.deal(tiles)
    actual = getattr(player, func)()
    actual.sort()
    return actual


def fail_msg(actual, expected):
    return f'''
        Actual:   {' '.join([string_list(t) for t in actual])}
        Expected: {' '.join([string_list(t) for t in expected])}
    '''


def winning_hand_fail_msg(actual, expected):
    a = ''
    for hand in actual:
        a += '\n' + ' '.join([string_list(t) for t in hand])
    return f'''
        Actual:   {a}
        Expected: {' '.join([string_list(t) for t in expected])}
    '''

class TestWinningHand(unittest.TestCase):

    def setup(self, tiles):
        player = Player("Test", None)
        player.update = Mock()
        for tile in tiles:
            player.deal(tile)
        return player

    def test_no_winning_hand(self):
        expected = []
        tiles = [
            Tile('R1'), Tile('R3'), Tile('R5'),
            Tile('G1'), Tile('G3'), Tile('G5'),
            Tile('B1'), Tile('B3'), Tile('B5'),
            Tile('R★'), Tile('G★'), Tile('B★'),
            Tile('MS'), Tile('MF')
        ]
        player = self.setup(tiles)
        actual = player.hand.winning_hands()
        self.assertListEqual(
            actual, expected, winning_hand_fail_msg(actual, expected))

    def test_all_runs_winning_hand(self):
        expected = [
            [Tile('R1'), Tile('R2'), Tile('R3')],
            [Tile('G1'), Tile('G2'), Tile('G3')],
            [Tile('B1'), Tile('B2'), Tile('B3')],
            [Tile('B7'), Tile('B8'), Tile('B9')],
            [Tile('MS'), Tile('MS')]
        ]
        expected.sort()
        tiles = [*expected[0], *expected[1], *
                 expected[2], *expected[3], *expected[4]]
        player = self.setup(tiles)
        actual = player.hand.winning_hands()
        self.assertListEqual(
            actual, [expected], winning_hand_fail_msg(actual, expected))

    def test_all_runs_revealed_group(self):
        expected = [
            [Tile('R1'), Tile('R2'), Tile('R3')],
            [Tile('G1'), Tile('G2'), Tile('G3')],
            [Tile('B1'), Tile('B2'), Tile('B3')],
            [Tile('B7'), Tile('B8'), Tile('B9')],
            [Tile('MS'), Tile('MS')]
        ]
        expected.sort()
        tiles = [*expected[0], *expected[1], *
                 expected[2], *expected[3], *expected[4]]
        player = self.setup(tiles)
        player.hand.reveal(expected[0])
        actual = player.hand.winning_hands()
        self.assertListEqual(
            actual, [expected], winning_hand_fail_msg(actual, expected))

    def test_all_runs_revealed_hand(self):
        expected = [
            [Tile('R1'), Tile('R2'), Tile('R3')],
            [Tile('G1'), Tile('G2'), Tile('G3')],
            [Tile('B1'), Tile('B2'), Tile('B3')],
            [Tile('B7'), Tile('B8'), Tile('B9')],
            [Tile('MS'), Tile('MS')]
        ]
        expected.sort()
        tiles = [*expected[0], *expected[1], *
                 expected[2], *expected[3], *expected[4]]
        player = self.setup(tiles)
        for group in expected[:-1]:
            player.hand.reveal(group)
        actual = player.hand.winning_hands()
        self.assertListEqual(
            actual, [expected], winning_hand_fail_msg(actual, expected))

    def test_all_triplets_winning_hand(self):
        expected = [
            [Tile('R1'), Tile('R1'), Tile('R1')],
            [Tile('G1'), Tile('G1'), Tile('G1')],
            [Tile('B1'), Tile('B1'), Tile('B1')],
            [Tile('B9'), Tile('B9'), Tile('B9')],
            [Tile('MS'), Tile('MS')]
        ]
        expected.sort()
        tiles = [*expected[0], *expected[1], *
                 expected[2], *expected[3], *expected[4]]
        player = self.setup(tiles)
        actual = player.hand.winning_hands()
        self.assertListEqual(
            actual, [expected], winning_hand_fail_msg(actual, expected))

    def test_mixed_winning_hand(self):
        expected = [
            [Tile('R1'), Tile('R2'), Tile('R3')],
            [Tile('G1'), Tile('G1'), Tile('G1')],
            [Tile('B1'), Tile('B2'), Tile('B3')],
            [Tile('B9'), Tile('B9'), Tile('B9')],
            [Tile('MS'), Tile('MS')]
        ]
        expected.sort()
        tiles = [*expected[0], *expected[1], *
                 expected[2], *expected[3], *expected[4]]
        player = self.setup(tiles)
        actual = player.hand.winning_hands()
        self.assertListEqual(
            actual, [expected], winning_hand_fail_msg(actual, expected))

    def test_multiple_winning_hands(self):
        tiles = [
            Tile('R1'), Tile('R2'), Tile('R3'),
            Tile('R1'), Tile('R2'), Tile('R3'),
            Tile('R1'), Tile('R2'), Tile('R3'),
            Tile('B9'), Tile('B9'), Tile('B9'),
            Tile('MS'), Tile('MS')
        ]
        player = self.setup(tiles)
        actual = player.hand.winning_hands()
        self.assertEqual(len(actual), 2)

    def test_performance_multiple_winning_hands(self):
        tiles = [
            Tile('R1'), Tile('R1'), Tile('R1'), Tile('R1'),
            Tile('R2'), Tile('R2'), Tile('R2'), Tile('R2'),
            Tile('R3'), Tile('R3'), Tile('R3'), Tile('R3'),
            Tile('R4'), Tile('R4')
        ]
        player = self.setup(tiles)
        actual = player.hand.winning_hands()

class TestMisc(unittest.TestCase):

    def test_no_overlap(self):
        a = {Tile('R1'), Tile('R1'), Tile('R1')}
        b = {Tile('R1'), Tile('R1'), Tile('R1')}
        self.assertTrue(no_overlap(a, b))

        o = Tile('R1')
        a = {o, Tile('R1'), Tile('R1')}
        b = {o, Tile('R1'), Tile('R1')}
        self.assertFalse(no_overlap(a, b))

    def test_remove_tiles_from_groups(self):
        a = Tile('R1')
        b = Tile('R2')
        c = Tile('R3')
        d = Tile('R4')
        groups = [
            [a, b, c],
            [a, a, a],
            [d, a, d],
            [d, d, b],
            [d, d, d],
        ]
        
        actual = Hand().remove_tiles_from_groups([a, b, c], groups)
        expected = [groups[4]]
        self.assertListEqual(actual, expected)

if __name__ == '__main__':
    unittest.main()
