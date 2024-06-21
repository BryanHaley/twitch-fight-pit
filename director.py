import traceback
import time
import threading
import pygame
from settings import Settings
from game_interface import GameInterface

class Director:
    """
    The director runs in another thread and coordinates active actors and animation sequences based on commands in a queue
    """
    def __init__(self, actors):
        self._command_queue = []
        self._actors = actors
        self._clock = pygame.time.Clock()
        self._quit = False
        self._director_thread = None
    
    def enqueue_command(self, command):
        self._command_queue.append(command)
    
    def quit(self):
        if not self._director_thread:
            return
        self._quit = True
        self._director_thread.join(10)

    def run(self):
        self._director_thread = threading.Thread(target=self.direct)
        self._director_thread.start()

    def direct(self):
        while not self._quit:
            # Get command off queue
            if len(self._command_queue) > 0:
                command = self._command_queue.pop(0)
                try:
                    if command["action"] == "pet":
                        self.direct_pet_interaction(command)
                    elif command["action"] == "squash":
                        self.direct_attack_interaction(command)
                    elif command["action"] == "heal":
                        self.direct_heal_interaction(command)
                    elif command["action"] == "defend":
                        self.direct_defend_interaction(command)
                    elif command["action"] == "faint":
                        self.direct_faint_interaction(command)
                    elif command["action"] == "update_skin":
                        self.direct_update_skin(command)
                    else:
                        print("Unrecognized command. Ignoring: {}: {}".format(command["action"], command))
                except:
                    print("Failed to carry out command: {}".format(command))
                    print(traceback.format_exc())
            else:
                # The clock will tick while commands are being directed so we don't want to double tick
                self._clock.tick(Settings.framerate)
    
    def puppet_actor(self, actor):
        self._actors[actor]["puppet"] = True

    def unpuppet_actor(self, actor):
        self._actors[actor]["puppet"] = False
    
    def make_actors_face_each_other(self, actor1, actor2):
        if actor1.get_x() < actor2.get_x():
            actor1.set_flipped(False)
            actor2.set_flipped(True)
        else:
            actor1.set_flipped(True)
            actor2.set_flipped(False)
    
    def position_actors_for_interaction(self, actor1, actor1_animator, actor2, actor2_animator):
        move_to_pos_running = "RUNNING"
        actor1_animator.set_animation("run")
        actor2_animator.set_animation("idle")
        # Make actors face each other
        self.make_actors_face_each_other(actor1, actor2)
        deltatime = 0
        # Move actor1 into position
        while move_to_pos_running != "SUCCESS":
            actor1_animator.play(deltatime)
            actor2_animator.play(deltatime)
            move_to_pos_running = actor1.move_to_point(
                (actor2.get_x()+(-Settings.sprite_spacing if actor1.get_x() < actor2.get_x() else Settings.sprite_spacing), 
                 Settings.sprite_elevation), 
                Settings.run_speed, 
                Settings.move_epsilon, 
                deltatime)
            self._clock.tick(Settings.framerate)
            deltatime = self._clock.get_time() * 0.001
    
    def play_interaction_animations(self, actor1_animator, actor2_animator, actor1_anim, actor2_anim):
        actor1_anim_playing = "RUNNING"
        actor2_anim_playing = "RUNNING"
        actor1_animator.set_animation(actor1_anim)
        actor2_animator.set_animation(actor2_anim)
        deltatime = 0
        while actor1_anim_playing == "RUNNING" or actor2_anim_playing == "RUNNING":
            actor1_anim_playing = actor1_animator.play(deltatime)
            actor2_anim_playing = actor2_animator.play(deltatime)
            self._clock.tick(Settings.framerate)
            deltatime = self._clock.get_time() * 0.001
    
    def direct_interaction(self, command, actor1_anim, actor2_anim):
        # Get actors and animators
        actor1 = self._actors[command["actor1"]]["actor"]
        actor2 = self._actors[command["actor2"]]["actor"]
        self.puppet_actor(command["actor1"])
        self.puppet_actor(command["actor2"])
        actor1_animator = self._actors[command["actor1"]]["animator"]
        actor2_animator = self._actors[command["actor2"]]["animator"]
        # Get actors into position
        self.position_actors_for_interaction(actor1, actor1_animator, actor2, actor2_animator)
        self.make_actors_face_each_other(actor1, actor2)
        # Play animations
        self.play_interaction_animations(actor1_animator, actor2_animator, actor1_anim, actor2_anim)
        # Return to idle
        actor1_animator.set_animation("idle")
        actor2_animator.set_animation("idle")
        self.unpuppet_actor(command["actor1"])
        self.unpuppet_actor(command["actor2"])
        return "SUCCESS"

    def direct_pet_interaction(self, command):
        self.direct_interaction(command, "pet", "get-pet")
    
    def direct_attack_interaction(self, command):
        self.direct_interaction(command, "attack", "get-attacked")
    
    def direct_defend_interaction(self, command):
        self.direct_interaction(command, "defend", "get-defended")
    
    def direct_heal_interaction(self, command):
        self.direct_interaction(command, "heal", "get-healed")
    
    def direct_faint_interaction(self, command):
        # Get actors and animators
        actor1 = self._actors[command["actor"]]["actor"]
        self.puppet_actor(command["actor"])
        actor1_animator = self._actors[command["actor"]]["animator"]
        actor1_anim_playing = "RUNNING"
        actor1_animator.set_animation("faint")
        # Play animation
        deltatime = 0
        while actor1_anim_playing == "RUNNING":
            actor1_anim_playing = actor1_animator.play(deltatime)
            self._clock.tick(Settings.framerate)
            deltatime = self._clock.get_time() * 0.001
        # Return to idle
        actor1_animator.set_animation("idle")
        self.unpuppet_actor(command["actor"])
        return "SUCCESS"
    
    def direct_update_skin(self, command):
        actor = self._actors[command["actor"]]["actor"]
        result = GameInterface.change_actor_skin(command["actor"])
        if result == "FAILURE":
            return "FAILURE"
        actor_animator = self._actors[command["actor"]]["animator"]
        actor_animator.set_animation("idle")
        return "SUCCESS"

if __name__ == "__main__":
    import pygame
    import sys
    import random
    from actor import Actor, Animator

    # Test director with some basic actions
    pygame.init()
    screen = pygame.display.set_mode((800,600))
    clock = pygame.time.Clock()
    deltatime = 0

    actor1 = Actor(100, 400)
    animator1 = Animator("test/director")
    animator1.set_animation("idle")
    actor2 = Actor(600, 400)
    animator2 = Animator("test/director")
    animator2.set_animation("idle")
    actor3 = Actor(200, 400)
    animator3 = Animator("test/director")
    animator3.set_animation("idle")
    actor4 = Actor(400, 400)
    animator4 = Animator("test/director")
    animator4.set_animation("idle")
    actors = {
        "zingochris": {
            "actor": actor1,
            "animator": animator1,
            "puppet": False
        },
        "aeomech": {
            "actor": actor2,
            "animator": animator2,
            "puppet": False
        },
        "spagettd": {
            "actor": actor3,
            "animator": animator3,
            "puppet": False
        },
        "lifeuhfindsaway": {
            "actor": actor4,
            "animator": animator4,
            "puppet": False
        }
    }
    director = Director(actors)
    director.run()

    director.enqueue_command({
        "actor1": "zingochris",
        "actor2": "aeomech",
        "action": "pet",
        "metadata": None
    })

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                director.quit()
                sys.exit()

        # Game logic
        for actor in actors:
            actor = actors[actor]
            if actor["puppet"]:
                continue
            move = True if random.randint(1,250) == 1 else False
            # If some actor is just sitting around, consider moving them
            if actor["animator"].get_animation_name() == "idle" and move:
                actor["animator"].set_animation("walk")
                actor["actor"].set_goal((random.randint(64, 700), 400))
            # If an actor has reached their goal, return them to idle
            if not actor["actor"].get_goal() and actor["animator"].get_animation_name() == "walk":
                actor["animator"].set_animation("idle")
            actor["actor"].run(deltatime)
        
        screen.fill((0,0,0))

        for actor in actors:
            actor = actors[actor]
            if not actor["puppet"]:
                actor["animator"].play(deltatime)
            actor["animator"].set_flipped(actor["actor"].get_flipped())
            screen.blit(
                pygame.transform.flip(actor["animator"].get_img(), actor["animator"].get_flipped(), False), 
                (actor["actor"].get_x()-actor["animator"].get_half_size(), actor["actor"].get_y()-actor["animator"].get_half_size()), 
                actor["animator"].get_crop_square()
            )

        pygame.display.flip()
        clock.tick(Settings.framerate)
        deltatime = clock.get_time() * 0.001