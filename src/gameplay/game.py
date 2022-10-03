from gameplay.player import Player
from gameplay.deck import Deck
from resource import log
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
    WAITING_FOR_DISCARD = 3
    WAITING_FOR_STEAL = 4

    HAND_SIZE = 14

    def __init__(self, socketio):
        self.socketio = socketio
        self.id = str(uuid4())
        self.state = Game.WAITING_FOR_PLAYERS
        self.players = []
        self.deck = Deck()
        self.turn = 0
        self.discard_pile = []
        self.thieves = []
        
    def add_player(self, name):
        log(f"Adding player {len(self.players)}: {name}")
        player = Player(name, self.socketio)
        player.is_party_leader = len(self.players) == 0
        self.players.append(player)
        return player
        
    def player(self, player_id):
        for player in self.players:
            if player.id == player_id:
                return player
        raise LookupError(f"Player with id '{player_id}' not found.")

    def set_turn(self, i):
        self.turn = i
        log(f"Set turn to {i}, {self.current_player().name}'s turn")

    def set_state(self, state):
        self.state = state
        states = {
            0: 'WAITING_FOR_PLAYERS',
            1: 'DEALING',
            2: 'DRAWING',
            3: 'WAITING_FOR_DISCARD',
            4: 'WAITING_FOR_STEAL',
        }
        log(f"Set state to {states[state]}")

    def player_can_discard(self, player):
        return (self.turn == self.indexof(player) and Game.WAITING_FOR_DISCARD) 
    
    def player_can_steal(self, player):
        return (player in self.thieves and Game.WAITING_FOR_STEAL)

    def indexof(self, player):
        return self.players.index(player)

    def discard(self, id, player):
        tile = player.discard(id)
        log(f"{player.name} is discarding {tile}")
        player.update()
        self.discard_pile.append(tile)
        self.thieves = []
        # update board
        for i in range(1, len(self.players)):
            index = (self.turn + i) % len(self.players)
            thief = self.players[index]
            steal_options = thief.steal_options(tile)
            if len(steal_options) > 0:
                self.set_state(Game.WAITING_FOR_STEAL)
                thief.prompt_steal(tile, steal_options)
                thief.set_can_play(True)
                self.thieves.append(thief)
        if self.state == Game.WAITING_FOR_STEAL:
            player.set_can_play(False)
        else:
            self.end_turn(player)


    def steal(self, group, player):
        player.steal(int(group))
        for p in self.players:
            p.end_steal()

    def deal(self):
        log(f"Dealing tiles to all players")
        self.set_state(Game.DEALING)
        self.deck.shuffle()
        for player in self.players:
            for i in range(Game.HAND_SIZE - 1):
                player.deal(self.deck.draw())
            player.update()
    
    def current_player(self):
        return self.players[self.turn]

    def start_turn(self):
        self.set_state(Game.DRAWING)
        tile = self.deck.draw()
        player = self.current_player()
        log(f"Starting {player.name}'s turn")
        player.deal(tile)
        player.set_can_play(True)
        player.update()
        self.set_state(self.WAITING_FOR_DISCARD)

    def end_turn(self, player):
        log(f"Ending {player.name}'s turn")
        self.set_turn((self.indexof(player) + 1) % len(self.players))
        player.set_can_play(False)
        self.start_turn()
    
    def end_steal(self, player):
        log(f"Ending {player.name}'s steal")
        player.update()
        self.set_state(self.WAITING_FOR_DISCARD)
        self.set_turn(self.indexof(player))