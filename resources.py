import pygame
import traceback
import sys

class _ResourceManager:
    def __init__(self):
        self._memo = {}

    def load_img(self, img_path):
        try:
            if not img_path in self._memo:
                self._memo[img_path] = pygame.image.load(img_path)
            return self._memo[img_path]
        except:
            # We could return none and try to handle it, but meh, just exit
            print("Failed to load image {}".format(img_path))
            sys.exit(traceback.format_exc())

ResourceManager = _ResourceManager()