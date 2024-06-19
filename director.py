import traceback
import time
import pygame

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
                except:
                    print("Failed to carry out command: {}".format(command))
                    print(traceback.format_exc())
            else:
                # The clock will tick while commands are being directed so we don't want to double tick
                self._clock.tick(60)
    
    def direct_pet_interaction(self, command):
        # Get actors and animators
        actor1 = self._actors[command["actor1"]]["actor"]
        actor2 = self._actors[command["actor2"]]["actor"]
        actor1_animator = self._actors[command["actor1"]]["animator"]
        actor2_animator = self._actors[command["actor2"]]["animator"]
        # Move actor1 into position
        move_to_pos_running = "RUNNING"
        actor1_animator.set_animation("run")
        actor2_animator.set_animation("idle")
        deltatime = 0
        while move_to_pos_running != "SUCCESS":
            actor1_animator.play(deltatime)
            actor2_animator.play(deltatime)
            # TODO: Configure floor height
            move_to_pos_running = actor1.move_to_point((actor2.get_x()-64, 400), 50, 5, deltatime)
            self._clock.tick(60)
            deltatime = self._clock.get_time() * 0.001
        # Play animations
        actor1_anim_playing = "RUNNING"
        actor2_anim_playing = "RUNNING"
        actor1_animator.set_animation("pet")
        actor2_animator.set_animation("get-pet")
        deltatime = 0
        while actor1_anim_playing == "RUNNING" or actor2_anim_playing == "RUNNING":
            actor1_anim_playing = actor1_animator.play(deltatime)
            actor2_anim_playing = actor2_animator.play(deltatime)
            self._clock.tick(60)
            deltatime = self._clock.get_time() * 0.001
        # Return to idle
        actor1_animator.set_animation("idle")
        actor2_animator.set_animation("idle")
        # TODO: Some sort of "being directed" flag on actors so we can return them back to the main thread's control
        return "SUCCESS"

if __name__ == "__main__":
    import pygame
    import sys
    import threading
    from actor import Actor, Animator

    # Test actor and animation by moving an animation around the screen
    pygame.init()
    screen = pygame.display.set_mode((800,600))
    clock = pygame.time.Clock()
    deltatime = 0

    actor1 = Actor(100, 400)
    animator1 = Animator("test/director")
    actor2 = Actor(600, 400)
    animator2 = Animator("test/director")
    actors = {
        "zingochris": {
            "actor": actor1,
            "animator": animator1
        },
        "aeomech": {
            "actor": actor2,
            "animator": animator2
        }
    }
    director = Director(actors)
    director.run()

    director.enqueue_command({
        "actor1": "zingochris",
        "actor2": "aeomech",
        "action": "pet"
    })

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                director.quit()
                sys.exit()
        
        # animator1.play(deltatime)
        # animator2.play(deltatime)

        screen.fill((0,0,0))
        screen.blit(animator1.get_img(), (actor1.get_x()-animator1.get_half_size(), actor1.get_y()-animator1.get_half_size()), animator1.get_crop_square())
        screen.blit(animator2.get_img(), (actor2.get_x()-animator2.get_half_size(), actor2.get_y()-animator2.get_half_size()), animator2.get_crop_square())
        pygame.display.flip()
        clock.tick(60)
        deltatime = clock.get_time() * 0.001