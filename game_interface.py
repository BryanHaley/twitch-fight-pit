import time
from actor import Actor, Animator
from settings import Settings

class _GameInterface:
    def __init__(self):
        self._actors = {}
        self._remove_queue = []
        self._director = None
    
    def add_actor(self, name, x):
        if name not in self._actors:
            actor = Actor(x, Settings.sprite_elevation)
            animator = Animator("skins/default")
            animator.set_animation("idle")
            self._actors[name] = {
                "actor": actor,
                "animator": animator,
                "puppet": False,
                "defended": False
            }

    def defend_actor(self, name):
        if name in self._actors:
            self._actors[name]["defended"] = True
    
    def undefend_actor(self, name):
        if name in self._actors:
            self._actors[name]["defended"] = False
    
    def is_actor_defended(self, name):
        if name in self._actors:
            return self._actors[name]["defended"]
        else:
            return False

    def run(self):
        if len(self._remove_queue) < 1:
            return
        # Don't delete from actors if this actor is currently being puppeted by the director
        if not self._actors[self._remove_queue[0]]["puppet"]:
            del self._actors[self._remove_queue.pop(0)]
    
    def enqueue_delete_actor(self, actor):
        self._remove_queue.append(actor)

    def enqueue_command(self, command):
        if self._director:
            self._director.enqueue_command(command)
    
    def set_director(self, director):
        self._director = director
    
    def get_actors(self):
        return self._actors


GameInterface = _GameInterface()