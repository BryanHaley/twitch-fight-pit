import os
import random
from actor import Actor, Animator
from settings import Settings
from nametag import Nametag
from skins import SkinOverrides

class _GameInterface:
    def __init__(self):
        self._actors = {}
        self._remove_queue = []
        self._director = None
    
    def add_actor(self, name, x):
        if name not in self._actors:
            # Create actor
            actor = Actor(x, Settings.sprite_elevation)
            # Determine skin to use
            animator = None
            override = SkinOverrides.get_override_for_name(name)
            if override:
                animator = Animator(override)
            else:
                path = os.path.join("skins", "special", name)
                if os.path.exists(path):
                    animator = Animator(path)
                else:
                    # Pick a random skin to use
                    skins = SkinOverrides.get_available_skins()
                    skin = random.choice(skins)
                    skin_path = os.path.join("skins", "random", skin)
                    animator = Animator(skin_path)
            # Sanity check
            if not animator:
                print("WARNING: Failed to select skin for {}".format(name))
            # Set animation
            animator.set_animation("idle")
            # Create actor
            self._actors[name] = {
                "actor": actor,
                "animator": animator,
                "puppet": False,
                "defended": False,
                "nametag": Nametag(name)
            }
    
    def change_actor_skin(self, name):
        if not name in self._actors:
            return "FAILURE"
        # Determine skin to use
        skin = SkinOverrides.get_override_for_name(name)
        if skin:
            animator = Animator(skin)
            self._actors[name]["animator"] = animator
            return "SUCCESS"
        return "FAILURE"

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