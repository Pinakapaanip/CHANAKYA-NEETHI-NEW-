from entities.npc import NPC


class Spy(NPC):
    def __init__(self, x, y):
        super().__init__(x, y, name="Spy", color=(76, 124, 89))
        self.revealed = False
