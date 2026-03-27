class TransitionSystem:
    def __init__(self, scene_manager):
        self.scene_manager = scene_manager

    def to_scene(self, scene_name):
        self.scene_manager.change_scene(scene_name)
