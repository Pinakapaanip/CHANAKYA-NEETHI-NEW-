from ui.objective_panel import ObjectivePanel
from ui.instruction_panel import InstructionPanel

class UISystem:
    def __init__(self, assets, state):
        self.objective_panel = ObjectivePanel(assets, state)
        self.instruction_panel = InstructionPanel(assets, state)

    def handle_event(self, event):
        pass

    def update(self):
        pass

    def draw(self, screen):
        self.objective_panel.draw(screen)
        self.instruction_panel.draw(screen)
