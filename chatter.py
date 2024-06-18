import pygame
import random
import time

TEXT_OFFSET = 0

AI_SCHEDULE_STARTS = {
    "IDLE": "IDLE",
    "WAIT": "IDLE",
    "WAIT_THEN_IDLE": "WAIT_RANDOM",
    "WANDER": "SET_RANDOM_TARGET",
    "ATTACK": "MOVE_TO_TARGET",
    "TAKE_DAMAGE": "TAKE_DAMAGE",
    "GET_HEALED": "GET_HEALED",
    "HEAL": "MOVE_TO_TARGET",
    "DEFEND": "MOVE_TO_TARGET",
    "GET_DEFENDED": "GET_DEFENDED",
    "PET": "MOVE_TO_TARGET",
    "GET_PETTED": "GET_PETTED",
    "FAINT": "FAINT"
}

class Chatter:

    def __init__(self, context, name):
        global TEXT_OFFSET
        self.xmax = context["screen_size"][0]-140
        self.rect = pygame.Rect(0,0,128,128)
        self.rect.x = random.randrange(140, self.xmax)
        self.rect.y = 400
        self.name_text = context["font"].render(name, True, (0, 0, 0))
        self.text_offset = TEXT_OFFSET
        TEXT_OFFSET += 20
        TEXT_OFFSET = TEXT_OFFSET % 80
        self.velocity = [0,0]
        self.schedule = "IDLE"
        self.task = "IDLE"
        self.task_status = "FINISHED"
        self.wait_end_time = 0
        self.target = None
        self.look_target = None
        self.flip = False
        self.actor_target = None
        self.counter_attack = False
        self.faint = False
        self.defended = False
        self.animation = Animator(context)
        self.set_schedule("WANDER")
    
    def get_text_offset(self):
        return self.text_offset

    def get_name_text(self):
        return self.name_text
    
    def set_defended(self, defended):
        self.defended = defended
    
    def get_defended(self):
        return self.defended

    def set_faint(self, faint):
        self.faint = faint

    def get_schedule(self):
        return self.schedule
    
    def get_task(self):
        return self.task
    
    def get_task_status(self):
        return self.task_status

    def set_schedule(self, schedule):
        self.task_status = "STARTING"
        self.task = AI_SCHEDULE_STARTS[schedule]
        self.schedule = schedule
    
    def set_counter_attack(self, counter):
        self.counter_attack = counter
    
    def attack(self, attack_target, counter, attacker_faint, victim_faint):
        self.action_on_actor(attack_target, "ATTACK")
        attack_target.set_counter_attack(counter)
        attack_target.set_faint(victim_faint)
        self.set_faint(attacker_faint)
    
    def heal(self, heal_target):
        self.action_on_actor(heal_target, "HEAL")
    
    def defend(self, defend_target):
        self.action_on_actor(defend_target, "DEFEND")
    
    def pet(self, pet_target):
        self.action_on_actor(pet_target, "PET")

    def action_on_actor(self, target, schedule):
        self.target = target.get_rect().centerx + (64 if random.randint(0,1) == 0 else -64)
        self.look_target = target.get_rect().centerx
        self.actor_target = target
        self.set_schedule(schedule)
        target.set_schedule("WAIT")

    def get_flip(self):
        return self.flip
    
    def run_schedule(self):
        if self.schedule == "IDLE" or self.schedule == "WAIT":
            self.animation.set_animation("IDLE")
            return
        elif self.schedule == "WANDER":
            self.animation.set_animation("IDLE")
            self.run_task("SET_RANDOM_TARGET", self.task_set_random_target, "MOVE_TO_TARGET")
            self.run_task("MOVE_TO_TARGET", self.task_move_to_target, "WAIT_RANDOM")
            self.run_task("WAIT_RANDOM", self.task_wait_random, "END")
            if self.task == "END":
                self.set_schedule("IDLE")
        elif self.schedule == "ATTACK":
            self.run_task("MOVE_TO_TARGET", self.task_move_to_target, "FACE_TARGET")
            self.run_task("FACE_TARGET", self.task_face_target, "ATTACK")
            self.run_task("ATTACK", self.task_attack, "WAIT_RANDOM")
            self.run_task("WAIT_RANDOM", self.task_wait_random, "END")
            if self.task == "END":
                self.set_schedule("IDLE")
        elif self.schedule == "TAKE_DAMAGE":
            self.run_task("TAKE_DAMAGE", self.task_take_damage, "WAIT_RANDOM")
            self.run_task("WAIT_RANDOM", self.task_wait_random, "END")
            if self.task == "END":
                self.set_schedule("IDLE")
        elif self.schedule == "HEAL":
            self.run_task("MOVE_TO_TARGET", self.task_move_to_target, "FACE_TARGET")
            self.run_task("FACE_TARGET", self.task_face_target, "HEAL")
            self.run_task("HEAL", self.task_heal, "WAIT_RANDOM")
            self.run_task("WAIT_RANDOM", self.task_wait_random, "END")
            if self.task == "END":
                self.set_schedule("IDLE")
        elif self.schedule == "GET_HEALED":
            self.run_task("GET_HEALED", self.task_get_healed, "WAIT_RANDOM")
            self.run_task("WAIT_RANDOM", self.task_wait_random, "END")
            if self.task == "END":
                self.set_schedule("IDLE")
        elif self.schedule == "DEFEND":
            self.run_task("MOVE_TO_TARGET", self.task_move_to_target, "FACE_TARGET")
            self.run_task("FACE_TARGET", self.task_face_target, "DEFEND")
            self.run_task("DEFEND", self.task_defend, "WAIT_RANDOM")
            self.run_task("WAIT_RANDOM", self.task_wait_random, "END")
            if self.task == "END":
                self.set_schedule("IDLE")
        elif self.schedule == "GET_DEFENDED":
            self.run_task("GET_DEFENDED", self.task_get_defended, "WAIT_RANDOM")
            self.run_task("WAIT_RANDOM", self.task_wait_random, "END")
            if self.task == "END":
                self.set_schedule("IDLE")
        elif self.schedule == "PET":
            self.run_task("MOVE_TO_TARGET", self.task_move_to_target, "FACE_TARGET")
            self.run_task("FACE_TARGET", self.task_face_target, "PET")
            self.run_task("PET", self.task_pet, "WAIT_RANDOM")
            self.run_task("WAIT_RANDOM", self.task_wait_random, "END")
            if self.task == "END":
                self.set_schedule("IDLE")
        elif self.schedule == "GET_PETTED":
            self.run_task("GET_PETTED", self.task_get_petted, "WAIT_RANDOM")
            self.run_task("WAIT_RANDOM", self.task_wait_random, "END")
            if self.task == "END":
                self.set_schedule("IDLE")
        elif self.schedule == "WAIT_THEN_IDLE":
            self.run_task("WAIT_RANDOM", self.task_wait_random, "END")
            if self.task == "END":
                self.set_schedule("IDLE")
        elif self.schedule == "FAINT":
            self.run_task("FAINT", self.task_faint, "END")
            if self.task == "END":
                self.set_schedule("IDLE")
        
        if self.velocity[0] < 0:
            self.flip = True
        elif self.velocity[0] > 0:
            self.flip = False

        if self.schedule == "WANDER" and self.velocity[0] != 0:
            self.animation.set_animation("WALK")

        self.move()
    
    def run_task(self, task, task_func, next_task):
        if self.task == task:
            task_func()
            if self.task_status == "FINISHED":
                self.task = next_task
                self.task_status = "STARTING"
    
    def task_set_random_target(self):
        self.target = random.randrange(140, self.xmax)
        self.task_status = "FINISHED"
    
    def task_move_to_target(self):
        if not self.target:
            return
        self.task_status = "RUNNING"
        self.velocity = [2 if self.target > self.rect.centerx else -2, 0]
        if abs(self.target-self.rect.centerx) < 5:
            self.velocity = [0,0]
            self.task_status = "FINISHED"
    
    def task_face_target(self):
        self.velocity = [0,0]
        if self.look_target < self.get_rect().centerx:
            self.flip = True
        else:
            self.flip = False
        self.task_status = "FINISHED"
    
    def task_attack(self):
        if self.task_status == "STARTING":
            self.actor_target.set_schedule("TAKE_DAMAGE")
        self.play_animation_as_task("ATTACK", 1)

        if self.faint and self.task_status == "FINISHED":
            self.set_schedule("FAINT")
    
    def task_heal(self):
        if self.task_status == "STARTING":
            self.actor_target.set_schedule("GET_HEALED")
        self.play_animation_as_task("HEAL", 1)
    
    def task_pet(self):
        if self.task_status == "STARTING":
            self.actor_target.set_schedule("GET_PETTED")
        self.play_animation_as_task("PET", 1)
    
    def task_defend(self):
        if self.task_status == "STARTING":
            self.actor_target.set_schedule("GET_DEFENDED")
        self.play_animation_as_task("DEFEND", 1)
    
    def task_wait_random(self):
        self.play_animation_as_task("IDLE", random.randrange(1, 5))
    
    def task_faint(self):
        self.play_animation_as_task("FAINT", 8)
        self.faint = False
    
    def task_take_damage(self):
        self.set_defended(False)
        if self.counter_attack:
            self.play_animation_as_task("COUNTER", 1)
        else:
            self.play_animation_as_task("DAMAGE", 1)
        
        if self.faint and self.task_status == "FINISHED":
            self.set_schedule("FAINT")
    
    def task_get_healed(self):
        self.play_animation_as_task("HEALED", 1)
    
    def task_get_petted(self):
        self.play_animation_as_task("PETTED", 1)
    
    def task_get_defended(self):
        self.set_defended(True)
        self.play_animation_as_task("DEFENDED", 1)
    
    def play_animation_as_task(self, anim, wait_time):
        self.velocity = [0,0]
        if self.task_status == "STARTING":
            self.wait_end_time = time.time() + wait_time
            self.animation.set_animation_frame(0)
            self.animation.set_animation(anim)
            self.task_status = "RUNNING"
        elif time.time() >= self.wait_end_time:
            self.task_status = "FINISHED"
    
    def move(self):
        self.rect = self.rect.move(self.velocity)
    
    def get_img(self):
        return self.animation.get_img()
    
    def get_crop_square(self):
        return self.animation.get_crop_square()

    def get_rect(self):
        return self.rect
    
    def get_velocity(self):
        return self.velocity

    def set_velocity(self, veloc):
        self.velocity = veloc

    def set_velocity_x(self, x):
        self.velocity[0] = x

    def set_velocity_y(self, y):
        self.velocity[1] = y


class Animator:
    def __init__(self, context, skin="default"):
        self.animations = {
            "IDLE": 0,
            "IDLE_SPECIAL": 1,
            "WALK": 2,
            "RUN": 3,
            "ATTACK": 4,
            "COUNTER": 5,
            "CRITICAL": 6,
            "DAMAGE": 7,
            "DEFEND": 8,
            "DEFENDED": 9,
            "HEAL": 10,
            "HEALED": 11,
            "PET": 12,
            "PETTED": 13,
            "FAINT": 14,
            "RESERVED2": 15
        }
        self.current_animation = "IDLE"
        self.current_frame = 0
        self.next_frame_time = time.time() + 1/12
        self.img = context["spritesheets"][skin]
        self.crop = (0,0,0,0)
    
    def set_animation(self, anim):
        self.current_animation = anim
    
    def get_animation_frame(self):
        return self.current_frame

    def set_animation_frame(self, frame):
        self.current_frame = frame
    
    def get_animation(self):
        return self.current_animation
    
    def get_img(self):
        return self.img
    
    def get_crop_square(self):
        if time.time() > self.next_frame_time:
            self.current_frame += 1
            self.next_frame_time = time.time() + 1/12
            if self.current_frame >= 12:
                self.current_frame = 0
        crop_x1 = 128 * self.current_frame
        crop_y1 = 128 * self.animations[self.current_animation]
        crop_x2 = 128
        crop_y2 = 128
        return crop_x1, crop_y1, crop_x2, crop_y2