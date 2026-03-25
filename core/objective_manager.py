class ObjectiveManager:
    def __init__(self, initial_objective=""):
        self.current_objective = initial_objective

    def set_objective(self, objective_text):
        self.current_objective = objective_text

    def get_objective(self):
        return self.current_objective
