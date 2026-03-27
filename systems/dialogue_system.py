import pygame
from ui.dialogue_box import DialogueBox

class DialogueSystem:
    def __init__(self, assets):
        self.dialogue_box = DialogueBox(assets)
        self.active = False
        self.dialogue = []
        self.index = 0
        self.speaker = None

    def start_dialogue(self, dialogue, speaker=None):
        self.dialogue = dialogue
        self.index = 0
        self.active = True
        self.speaker = speaker
        self.dialogue_box.set_dialogue(dialogue, speaker)

    def handle_event(self, event):
        if self.active and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.index += 1
            if self.index >= len(self.dialogue):
                self.active = False
                self.dialogue_box.hide()
            else:
                self.dialogue_box.set_dialogue(self.dialogue, self.speaker, self.index)

    def update(self):
        pass

    def draw(self, screen):
        if self.active:
            self.dialogue_box.draw(screen)
