class BaseScene:
    def __init__(self, game):
        self.game = game

    def handle_event(self, event):
        raise NotImplementedError

    def update(self, dt):
        raise NotImplementedError

    def draw(self, surface):
        raise NotImplementedError
