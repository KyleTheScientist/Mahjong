import unittest
import colorama
from mahjong import Game, Player, Tile, string_list, no_overlap

colorama.init()


def triplets(tiles):
    return player_function('triplets', tiles)


def runs(tiles):
    return player_function('runs', tiles)


def winning_hands(tiles):
    return player_function('winning_hands', tiles)


def player_function(func, tiles):
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

class TestStealing(unittest.TestCase):

    def test_no_steal(self):
        player = Player("A", 0)
        player.deal(
            [Tile('R1'), Tile('R3'), Tile('R5'),
            Tile('G1'), Tile('G3'), Tile('G5'),
            Tile('B1'), Tile('B3'), Tile('B5'),
            Tile('RD'), Tile('GD'), Tile('BD'),
            Tile('MN')]
        )
        actual = player.stealportunities(Tile('YD'))
        expected = []
        self.assertListEqual(actual, expected, msg=fail_msg(actual, expected))

    def test_steal_triplet(self):
        player = Player("A", 0)
        a, b, c =  Tile('RD'), Tile('RD'), Tile('RD')
        player.deal([
            a, b,
            Tile('R1'), Tile('R2'), Tile('R5'),
            Tile('G1'), Tile('G3'), Tile('G5'),
            Tile('B1'), Tile('B3'), Tile('B5'),
            Tile('MN'), Tile('ME') 
        ])
        actual = player.stealportunities(c)
        expected = [[a, b, c]]
        self.assertListEqual(actual, expected, msg=fail_msg(actual, expected))

    def test_steal_run(self):
        player = Player("A", 0)
        a, b, c =  Tile('R1'), Tile('R2'), Tile('R3')
        player.deal([
            a, b,
            Tile('R5'), Tile('R7'), Tile('R9'),
            Tile('G1'), Tile('G2'), Tile('G3'),
            Tile('B1'), Tile('B3'), Tile('B5'),
            Tile('MN'), Tile('ME') 
        ])
        actual = player.stealportunities(c)
        expected = [[a, b, c]]
        self.assertListEqual(actual, expected, msg=fail_msg(actual, expected))

    def test_steal_mixed(self):
        player = Player("A", 0)
        a, b, c =  Tile('R1'), Tile('R1'), Tile('R1')
        d, e =  Tile('R2'), Tile('R3')
        player.deal([
            a, b, d, e,
            Tile('R5'), Tile('R7'), Tile('R9'),
            Tile('G1'), Tile('G3'), Tile('G5'),
            Tile('B1'), Tile('B3'), Tile('B5'),
            Tile('MN'), Tile('ME') 
        ])
        actual = player.stealportunities(c)
        expected = [[a, b, c], [c, d, e]]
        actual.sort()
        expected.sort()
        self.assertListEqual(actual, expected, msg=fail_msg(actual, expected))


class TestWinningHand(unittest.TestCase):
    def test_no_winning_hand(self):
        expected = []
        tiles = [
            Tile('R1'), Tile('R3'), Tile('R5'),
            Tile('G1'), Tile('G3'), Tile('G5'),
            Tile('B1'), Tile('B3'), Tile('B5'),
            Tile('RD'), Tile('GD'), Tile('BD'),
            Tile('MN'), Tile('ME')
        ]
        actual = winning_hands(tiles)
        self.assertListEqual(
            actual, expected, winning_hand_fail_msg(actual, expected))

    def test_all_runs_winning_hand(self):
        expected = [
            [Tile('R1'), Tile('R2'), Tile('R3')],
            [Tile('G1'), Tile('G2'), Tile('G3')],
            [Tile('B1'), Tile('B2'), Tile('B3')],
            [Tile('B7'), Tile('B8'), Tile('B9')],
            [Tile('MN'), Tile('MN')]
        ]
        expected.sort()
        tiles = [*expected[0], *expected[1], *
                 expected[2], *expected[3], *expected[4]]
        actual = winning_hands(tiles)
        self.assertListEqual(
            actual, [expected], winning_hand_fail_msg(actual, expected))

    def test_all_triplets_winning_hand(self):
        expected = [
            [Tile('R1'), Tile('R1'), Tile('R1')],
            [Tile('G1'), Tile('G1'), Tile('G1')],
            [Tile('B1'), Tile('B1'), Tile('B1')],
            [Tile('B9'), Tile('B9'), Tile('B9')],
            [Tile('MN'), Tile('MN')]
        ]
        expected.sort()
        tiles = [*expected[0], *expected[1], *
                 expected[2], *expected[3], *expected[4]]
        actual = winning_hands(tiles)
        self.assertListEqual(
            actual, [expected], winning_hand_fail_msg(actual, expected))

    def test_mixed_winning_hand(self):
        expected = [
            [Tile('R1'), Tile('R2'), Tile('R3')],
            [Tile('G1'), Tile('G1'), Tile('G1')],
            [Tile('B1'), Tile('B2'), Tile('B3')],
            [Tile('B9'), Tile('B9'), Tile('B9')],
            [Tile('MN'), Tile('MN')]
        ]
        expected.sort()
        tiles = [*expected[0], *expected[1], *
                 expected[2], *expected[3], *expected[4]]
        actual = winning_hands(tiles)
        self.assertListEqual(
            actual, [expected], winning_hand_fail_msg(actual, expected))

    def test_multiple_winning_hands(self):
        tiles = [
            Tile('R1'), Tile('R2'), Tile('R3'),
            Tile('R1'), Tile('R2'), Tile('R3'),
            Tile('R1'), Tile('R2'), Tile('R3'),
            Tile('B9'), Tile('B9'), Tile('B9'),
            Tile('MN'), Tile('MN')
        ]
        actual = winning_hands(tiles)
        self.assertEqual(len(actual), 2)


class TestTriplets(unittest.TestCase):

    def test_no_triplets(self):
        expected = []
        tiles = []
        for i in [1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 2, 3, 4, 5]:
            tiles.append(Tile('B' + str(i)))

        actual = triplets(tiles)
        self.assertListEqual(actual, expected, fail_msg(actual, expected))

    def test_one_triplet(self):
        expected = [
            [
                Tile('G1'),
                Tile('G1'),
                Tile('G1'),
            ],
        ]
        tiles = [
            *expected[0],
            Tile('R1'), Tile('R1'),
            Tile('R2'), Tile('R2'),
            Tile('R3'), Tile('R3'),
            Tile('R4'), Tile('R4'),
            Tile('R5'), Tile('R6'), Tile('R7'),
        ]
        actual = triplets(tiles)
        self.assertListEqual(
            actual, expected, msg=fail_msg(actual, expected))

    def test_many_triplets(self):
        expected = [
            [Tile('G1'), Tile('G1'), Tile('G1')],
            [Tile('R2'), Tile('R2'), Tile('R2')],
            [Tile('BD'), Tile('BD'), Tile('BD')],
            [Tile('MW'), Tile('MW'), Tile('MW')]
        ]
        expected.sort()

        tiles = [
            * expected[0], * expected[1],
            * expected[2], * expected[3],
            Tile('G6'), Tile('G6')
        ]

        actual = triplets(tiles)
        self.assertListEqual(
            actual, expected, msg=fail_msg(actual, expected))

    def test_quadruplet(self):
        expected = [[Tile('G1'), Tile('G1'), Tile('G1')]]
        tiles = [
            Tile('G1'),
            Tile('R1'), Tile('R1'),
            Tile('R2'), Tile('R2'),
            Tile('R3'), Tile('R3'),
            Tile('R4'), Tile('R4'),
            Tile('R5'), Tile('R6')
        ]
        tiles.extend(expected[0])

        actual = triplets(tiles)
        self.assertListEqual(
            actual, expected, msg=fail_msg(actual, expected))


class TestRuns(unittest.TestCase):

    def test_no_runs(self):
        expected = []
        tiles = [
            Tile('R1'), Tile('G1'), Tile('B1'),
            Tile('R3'), Tile('G3'), Tile('B3'),
            Tile('R5'), Tile('G5'), Tile('B5'),
            Tile('R7'), Tile('G7'), Tile('B7'),
            Tile('RD'), Tile('RD')
        ]
        actual = runs(tiles)
        self.assertListEqual(
            actual, expected, msg=fail_msg(actual, expected))

    def test_one_run(self):
        expected = [[Tile('R1'), Tile('R2'), Tile('R3')]]
        tiles = [
            *expected[0],
            Tile('R5'), Tile('G5'), Tile('B5'),
            Tile('R7'), Tile('G7'), Tile('B7'),
            Tile('R9'), Tile('G9'), Tile('B9'),
            Tile('RD'), Tile('RD')
        ]

        expected.sort()
        actual = runs(tiles)
        self.assertListEqual(
            actual, expected, msg=fail_msg(actual, expected))

    def test_overlapping_runs(self):
        a, b, c, d = Tile('R1'), Tile('R2'), Tile('R3'), Tile('R4')
        expected = [[a, b, c], [b, c, d]]
        tiles = [
            a, b, c, d, Tile('RD'), Tile('RD'), Tile(
                'RD'), Tile('RD'), Tile('RD'),
            Tile('RD'), Tile('RD'), Tile('RD'), Tile('RD'), Tile('RD')
        ]

        expected.sort()
        actual = runs(tiles)
        self.assertListEqual(
            actual, expected, msg=fail_msg(actual, expected))

    def test_duplicate_runs(self):
        a, b, c, d = Tile('R1'), Tile('R2'), Tile('R3'), Tile('R3')
        expected = [[a, b, c], [a, b, d]]
        tiles = [
            a, b, c, d, Tile('RD'), Tile('RD'), Tile(
                'RD'), Tile('RD'), Tile('RD'),
            Tile('RD'), Tile('RD'), Tile('RD'), Tile('RD'), Tile('RD')
        ]

        expected.sort()
        actual = runs(tiles)
        self.assertListEqual(
            actual, expected, msg=fail_msg(actual, expected))

    def test_doubled_runs(self):
        a, b, c, d, e, f = Tile('R1'), Tile('R1'), Tile(
            'R2'), Tile('R2'), Tile('R3'), Tile('R3')
        tiles = [
            a, b, c, d, e, f, Tile('RD'), Tile('RD'), Tile('RD'),
            Tile('RD'), Tile('RD'), Tile('RD'), Tile('RD'), Tile('RD')
        ]

        actual = runs(tiles)
        self.assertEqual(len(actual), 8)


class TestMisc(unittest.TestCase):

    def test_no_overlap(self):
        a = [Tile('R1'), Tile('R1'), Tile('R1')]
        b = [Tile('R1'), Tile('R1'), Tile('R1')]
        self.assertTrue(no_overlap(a, b))

        o = Tile('R1')
        a = [o, Tile('R1'), Tile('R1')]
        b = [o, Tile('R1'), Tile('R1')]
        self.assertFalse(no_overlap(a, b))


if __name__ == '__main__':
    unittest.main()
