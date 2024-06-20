import pygame
import sys
import threading
import random
from actor import Actor, Animator
from director import Director

class _GameInterface:
    def __init__(self):
        self._actors = {}
        self._remove_queue = []
        self._director = None
    
    def add_actor(self, name, x):
        actor = Actor(x, 400)
        animator = Animator("test/director")
        animator.set_animation("idle")
        if name not in self._actors:
            self._actors[name] = {
                "actor": actor,
                "animator": animator,
                "puppet": False
            }

    def run(self):
        if len(self._remove_queue) < 1:
            return
        # Don't delete from actors if this actor is currently being puppeted by the director
        if not self._actors[self._remove_queue[0]]["puppet"]:
            del self._actors[self._remove_queue.pop(0)]
    
    def get_actors(self):
        return self._actors
    
    def set_director(self, director):
        self._director = director
    
    def enqueue_delete_actor(self, actor):
        self._remove_queue.append(actor)

    def enqueue_command(self, command):
        if self._director:
            self._director.enqueue_command(command)


GameInterface = _GameInterface()

if __name__ == "__main__":
    # Test actor and animation by moving an animation around the screen
    pygame.init()
    screen = pygame.display.set_mode((800,600))
    clock = pygame.time.Clock()
    deltatime = 0

    GameInterface.add_actor("zingochris", 100)
    GameInterface.add_actor("aeomech", 700)
    GameInterface.add_actor("spagettd", 550)
    GameInterface.add_actor("lifeuhfindsaway", 240)

    director = Director(GameInterface.get_actors())
    director.run()
    GameInterface.set_director(director)

    GameInterface.enqueue_command({
        "actor1": "zingochris",
        "actor2": "aeomech",
        "action": "pet",
        "metadata": None
    })

    GameInterface.enqueue_delete_actor("zingochris")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                director.quit()
                sys.exit()
        
        GameInterface.run()

        # Game logic
        for actor in GameInterface.get_actors():
            actor = GameInterface.get_actors()[actor]
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

        for actor in GameInterface.get_actors():
            actor = GameInterface.get_actors()[actor]
            if not actor["puppet"]:
                actor["animator"].play(deltatime)
            actor["animator"].set_flipped(actor["actor"].get_flipped())
            screen.blit(
                pygame.transform.flip(actor["animator"].get_img(), actor["animator"].get_flipped(), False), 
                (actor["actor"].get_x()-actor["animator"].get_half_size(), actor["actor"].get_y()-actor["animator"].get_half_size()), 
                actor["animator"].get_crop_square()
            )

        pygame.display.flip()
        clock.tick(60)
        deltatime = clock.get_time() * 0.001