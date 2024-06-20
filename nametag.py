from settings import Settings

class Nametag:
    def __init__(self, name):
        self._name = name
        self._img = Settings.nametag_font.render(name, Settings.nametag_antialias, Settings.nametag_color)
    
    def get_img(self):
        return self._img

    def blit(self, screen, actors):
        # Set our initial location
        our_actor = actors[self._name]
        x = our_actor["actor"].get_x()
        y = our_actor["actor"].get_y()-our_actor["animator"].get_half_size()
        # If there are other actors to the right overlapping us, move up
        x_max_bound = x+self._img.get_rect().width/2
        overlaps = 0
        for actor in actors:
            actor_name = actor
            if actor_name == self._name:
                continue
            actor = actors[actor]
            if actor["actor"].get_x() < x:
                continue
            # Check bounds
            actor_x_min_bound = actor["actor"].get_x()-actor["nametag"].get_img().get_rect().width/2
            if actor_x_min_bound < x_max_bound:
                overlaps += 1
        # Limit y so it doesn't just go to the top of the screen
        y -= (overlaps%Settings.nametag_overlap_limit)*(Settings.nametag_font_size+2)
        # Now blit at our final position
        screen.blit(self._img, (int(x-self._img.get_rect().width/2), int(y-self._img.get_rect().height)), self._img.get_rect())