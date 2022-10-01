from uuid import uuid4

class Player:
    def __init__(self, name):
        self.name = name
        self.id = str(uuid4())
        self.discards = []
        self.hand = Hand()

    def deal(self, tile):
        self.hand.hidden.append(tile)

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
    
