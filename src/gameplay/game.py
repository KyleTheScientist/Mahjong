from gameplay.player import Player
from gameplay.deck import Deck
from uuid import uuid4

# States
#     - Pre-Game
#         + Waiting for players
#         + Dealing
#     - In-Game
#         + Drawing
#         + Waiting for discard / win
#         + Waiting for steal
#     - Post-Game
#         + Waiting for restart

class Game:
    WAITING_FOR_PLAYERS = 0
    DEALING = 1
    DRAWING = 2
    WAITING_FOR_PLAYER = 3
    WAITING_FOR_STEAL = 4

    def __init__(self):
        self.id = str(uuid4())
        self.state = Game.WAITING_FOR_PLAYERS
        self.players = {}
        self.deck = Deck()
        
    def add_player(self, name):
        player = Player(name)
        self.players[player.id] = player
        print(player.id)
        return player
        
    def player(self, player_id):
        return self.players[player_id]