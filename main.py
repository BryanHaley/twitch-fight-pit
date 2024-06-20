import pygame
import sys
import threading
import random
from actor import Actor, Animator
from director import Director

if __name__ == "__main__":
    # Test actor and animation by moving an animation around the screen
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
        clock.tick(60)
        deltatime = clock.get_time() * 0.001