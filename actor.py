import math
import os
import sys
import random
import traceback
from resources import ResourceManager

class Actor:
    """
    An actor is a 2D point that can move itself in space.
    """
    def __init__(self, x=0, y=0):
        self._x = x
        self._y = y

    def move_to_point(self, point, speed, epsilon, deltatime):
        # Calculate the vector between self and the point
        vec_x = point[0]-self._x
        vec_y = point[1]-self._y
        magnitude = math.sqrt(vec_x*vec_x + vec_y*vec_y)
        # Normalize the vector
        vec_x_norm = vec_x/magnitude
        vec_y_norm = vec_y/magnitude
        # If we're not close enough to the point
        if abs(self._x-point[0]) > epsilon or abs(self._y-point[1]) > epsilon:
            # Move along the vector by speed
            self._x += speed * deltatime * vec_x_norm
            self._y += speed * deltatime * vec_y_norm
            return "RUNNING"
        # Otherwise, we're at the point, so return success
        return "SUCCESS"
    
    def get_x(self):
        return self._x
    
    def get_y(self):
        return self._y

    def get_position(self):
        return (self._x, self._y)

class Animation:
    """
    An animation is a sequence of images that can play. It does not have a position in 2D space; it returns an image and a crop square.
    """
    def __init__(self, spritesheet, framerate, frames, loop, size):
        self._current_frame = 0
        self._img = spritesheet
        self._frames = frames
        self._framerate = framerate
        self._size = size
        self._timer = 0
        self._loop = loop
    
    def play(self, deltatime):
        if self._current_frame == self._frames-1:
            if self._loop:
                self.reset()
            else:
                return "SUCCESS"
        self._timer += deltatime
        if self._timer > self._framerate*(self._current_frame+1):
            self._current_frame += 1
        return "SUCCESS" if self._current_frame == self._frames else "RUNNING"
    
    def reset(self):
        self._timer = 0
        self._current_frame = 0
        return "SUCCESS"

    def get_crop_square(self):
        crop_x1 = self._size * self._current_frame
        crop_y1 = 0
        crop_x2 = self._size
        crop_y2 = self._size
        return crop_x1, crop_y1, crop_x2, crop_y2
    
    def get_img(self):
        return self._img
    
    def get_size(self):
        return self._size
    
    def get_half_size(self):
        return self._size/2

class Animator:
    """
    An animator wraps Animation functions and can swap out animations. It also loads images and instantiates animations from a path.
    """
    def __init__(self, path):
        # Build a dictionary of animations
        # Each animation will have a list of possible animations that might play
        # when it's selected
        self._animations = {}
        self._current_animation = None
        # Load all the animation sprite sheets in the path
        paths = os.listdir(path)
        for item in paths:
            try:
                item = os.path.join(path, item)
                if not os.path.isfile(item):
                    continue
                filename = os.path.basename(item)
                if not (filename[-4:] == ".PNG" or filename[-4:] == ".png"):
                    continue
                if "_" in filename:
                    filename_parts = filename[:-4].split("_")
                    if len(filename_parts) < 3:
                        continue
                    # Find animation base name, framerate, and looping
                    anim_basename = filename_parts[0]
                    anim_framerate = 1/float(filename_parts[1])
                    anim_loop = True if filename_parts[2].lower() == "true" else False
                else:
                    # Assume some defaults
                    anim_basename = filename[:-4]
                    anim_framerate = 1/12
                    anim_loop = False
                # Load image for animation
                anim_img = ResourceManager.load_img(item)
                # Determine anim size and number of frames
                anim_size = anim_img.get_rect().height
                anim_frames = int(anim_img.get_rect().width/anim_size)
                # Create the animation
                anim = Animation(anim_img, anim_framerate, anim_frames, anim_loop, anim_size)
                # Instantiate a list for this animation name if it doesn't exist
                if not anim_basename in self._animations:
                    self._animations[anim_basename] = []
                # Add this animation to the list
                self._animations[anim_basename] += [anim]
                # Set the default animation if there is none
                if not self._current_animation:
                    self._current_animation = self._animations[anim_basename][0]
            except:
                print("Failed to create animation from {} (is the filename formatted correctly?)".format(item))
                sys.exit(traceback.format_exc())
    
    def set_animation(self, name, index=-1, reset=True):
        """
        Sets the animation by name. If index is less than zero (default), a random animation will be chosen from the list for the name.
        """
        # Sanity check
        if (name not in self._animations or
            index >= len(self._animations[name])):
            return "FAILURE"
        # Pick a random animation if not set
        if index < 0:
            index = random.randint(0, len(self._animations[name])-1)
        # Set the animation
        self._current_animation = self._animations[name][index]
        if reset:
            self._current_animation.reset()
    
    def play(self, deltatime):
        if not self._current_animation:
            return "FAILURE"
        return self._current_animation.play(deltatime)
    
    def reset(self):
        if not self._current_animation:
            return "FAILURE"
        return self._current_animation.reset()
    
    def get_img(self):
        if not self._current_animation:
            return "FAILURE"
        return self._current_animation.get_img()
    
    def get_crop_square(self):
        if not self._current_animation:
            return "FAILURE"
        return self._current_animation.get_crop_square()
    
    def get_size(self):
        if not self._current_animation:
            return "FAILURE"
        return self._current_animation.get_size()

    def get_half_size(self):
        if not self._current_animation:
            return "FAILURE"
        return self._current_animation.get_half_size()
    

if __name__ == "__main__":
    import pygame
    import sys

    # Test actor and animation by moving an animation around the screen
    pygame.init()
    screen = pygame.display.set_mode((800,600))
    clock = pygame.time.Clock()
    deltatime = 0

    actor = Actor()
    animator = Animator("test/animations")
    point = (random.randint(400, 800), random.randint(300, 600))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        
        actor_result = actor.move_to_point(point, 100, 5, deltatime)
        if actor_result == "SUCCESS":
            point = (random.randint(0, 800), random.randint(0, 600))
            animator.set_animation("animtest")
        animator.play(deltatime)

        screen.fill((0,0,0))
        screen.blit(animator.get_img(), (actor.get_x()-animator.get_half_size(), actor.get_y()-animator.get_half_size()), animator.get_crop_square())
        pygame.display.flip()
        clock.tick(60)
        deltatime = clock.get_time() * 0.001