import pygame
import sys
import random
import time
import threading
import traceback
import asyncio
from director import Director
from game_interface import GameInterface
from twitch_interface import TwitchInterface
from settings import Settings
from resources import ResourceManager
from twitch import run_twitch_handler

def start_twitch_thread():
    asyncio.run(run_twitch_handler())

if __name__ == "__main__":
    # Init pygame
    pygame.init()
    pygame.font.init()

    # Init settings
    Settings.init_from_file("settings.json")

    # Init some state
    screen = pygame.display.set_mode(Settings.screen_size)
    clock = pygame.time.Clock()
    shield_img = ResourceManager.load_img("shield.png")
    deltatime = 0

    # Init director
    director = Director(GameInterface.get_actors())
    director.run()
    GameInterface.set_director(director)

    # Set up twitch interface
    # TODO -- These are all probably unnecessary and can just be used from Settings directly
    TwitchInterface.set_app_id(Settings.app_id)
    TwitchInterface.set_app_secret(Settings.app_secret)
    TwitchInterface.set_target_channel(Settings.target_channel)
    TwitchInterface.set_ignore_list(Settings.ignore_list)
    TwitchInterface.set_chatter_default_health(Settings.default_health)

    # Add a chatter to test with if needed
    if Settings.debug:
        for i in range(Settings.debug_characters):
            TwitchInterface.add_chatter("testma" + (str(i) if i > 0 else ""))
    TwitchInterface.add_chatter(TwitchInterface.get_target_channel())

    # Start twitch handling thread
    twitch_thread = threading.Thread(target=start_twitch_thread, args=[])
    twitch_thread.start()

    # Game loop
    while True:
        try:
            # Handle quit event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    director.quit()
                    TwitchInterface.quit()
                    twitch_thread.join(10)
                    sys.exit()
            
            # Run game interface logic
            GameInterface.run()

            # Game logic
            for actor in GameInterface.get_actors():
                actor = GameInterface.get_actors()[actor]
                # Don't mess with actors that are currently being puppeted by the director
                if actor["puppet"]:
                    continue
                # Decide if we want this actor to move or not (if it's sitting around)
                move = True if random.randint(1,Settings.move_chance) == 1 else False
                # If some actor is just sitting around, consider moving them
                if actor["animator"].get_animation_name() == "idle" and move:
                    actor["animator"].set_animation("walk")
                    actor["actor"].set_goal((random.randint(Settings.sprite_spacing, Settings.screen_width-Settings.sprite_spacing), Settings.sprite_elevation))
                # If an actor has reached their goal, return them to idle
                if not actor["actor"].get_goal() and actor["animator"].get_animation_name() == "walk":
                    actor["animator"].set_animation("idle")
                # Run actor logic
                actor["actor"].run(deltatime)
            
            # Rendering logic
            # Blank screen
            screen.fill(Settings.background_color)

            # Iterate through actors
            for actor in GameInterface.get_actors():
                actor_name = actor
                actor = GameInterface.get_actors()[actor]
                # Animate non-puppeted actors (puppeted actors get animated by the director)
                if not actor["puppet"]:
                    anim_status = actor["animator"].play(deltatime)
                    # If playing a non-looping animation and it's finished, return to idle
                    if anim_status != "RUNNING":
                        actor["animator"].set_animation("idle")
                # Set flipped status of the animator using the actor's flipped status
                actor["animator"].set_flipped(actor["actor"].get_flipped())
                # Blit actor onto screen if the timeout hasn't elapsed
                if not actor["puppet"]:
                    if (not Settings.rendering_timeout or 
                        time.time() < TwitchInterface.get_last_command_time() + Settings.rendering_timeout):
                        if GameInterface.is_actor_defended(actor_name):
                            screen.blit(
                                shield_img, 
                                (actor["actor"].get_x()-shield_img.get_rect().width/2, actor["actor"].get_y()-shield_img.get_rect().height/2), 
                                shield_img.get_rect()
                            )
                        screen.blit(
                            pygame.transform.flip(actor["animator"].get_img(), actor["animator"].get_flipped(), False), 
                            (actor["actor"].get_x()-actor["animator"].get_half_size(), actor["actor"].get_y()-actor["animator"].get_half_size()), 
                            actor["animator"].get_crop_square()
                        )
                        actor["nametag"].blit(screen, GameInterface.get_actors())
            # Draw the puppeted actors on top
            for actor in GameInterface.get_actors():
                actor_name = actor
                actor = GameInterface.get_actors()[actor]
                # Blit actor onto screen if the timeout hasn't elapsed
                if actor["puppet"]:
                    if (not Settings.rendering_timeout or 
                        time.time() < TwitchInterface.get_last_command_time() + Settings.rendering_timeout):
                        if GameInterface.is_actor_defended(actor_name):
                            screen.blit(
                                shield_img, 
                                (actor["actor"].get_x()-shield_img.get_rect().width/2, actor["actor"].get_y()-shield_img.get_rect().height/2), 
                                shield_img.get_rect()
                            )
                        screen.blit(
                            pygame.transform.flip(actor["animator"].get_img(), actor["animator"].get_flipped(), False), 
                            (actor["actor"].get_x()-actor["animator"].get_half_size(), actor["actor"].get_y()-actor["animator"].get_half_size()), 
                            actor["animator"].get_crop_square()
                        )
                        actor["nametag"].blit(screen, GameInterface.get_actors())

            # Flip buffers
            pygame.display.flip()

            # Tick time
            clock.tick(Settings.framerate)
            deltatime = clock.get_time() * 0.001
        except RuntimeError:
            print(traceback.format_exc())