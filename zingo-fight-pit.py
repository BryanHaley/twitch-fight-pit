import sys
import pygame
import time
import threading
import json
import asyncio
import os
import traceback
from chatter import Chatter
from twitch import run_twitch_handler, set_funcs

RENDERING_TIMEOUT_SECONDS = 300
LAST_COMMAND_TIME = time.time()

context = {}
chatters = {}
SpriteSheets = {}
background = 0, 255, 0

def start_twitch_handler_thread(context):
    asyncio.run(run_twitch_handler(context))

def load_sheets_from_folder():
    global SpriteSheets
    files = os.listdir("skins")
    for file in files:
        file = os.path.join("skins", file)
        try:
            if os.path.exists(file) and os.path.isfile(file) and (file[-3:] == "png" or file[-3:] == "PNG"):
                spritesheet_name = os.path.basename(file)[:-4]
                print("Loading spritesheet: {}".format(spritesheet_name))
                SpriteSheets[spritesheet_name] = pygame.image.load(file)
        except:
            print(traceback.format_exc())

def read_settings():
    global background
    global RENDERING_TIMEOUT_SECONDS
    try:
        with open("settings.json", "r") as settings_json_file:
            settings_json = json.load(settings_json_file)
            for item in settings_json:
                context[item] = settings_json[item]
            context["screen_size"] = settings_json["SCREEN_WIDTH"], settings_json["SCREEN_HEIGHT"]
            background = settings_json["BACKGROUND_COLOR"][0], settings_json["BACKGROUND_COLOR"][1], settings_json["BACKGROUND_COLOR"][2]
            RENDERING_TIMEOUT_SECONDS = settings_json["RENDERING_TIMEOUT_SECONDS"]
    except:
        sys.exit("Failed to parse settings.json -- it is probably formatted incorrectly or missing key-value pairs. Exception:\n" + traceback.format_exc())

def set_last_command_time(time):
    global LAST_COMMAND_TIME
    LAST_COMMAND_TIME = time

def add_chatter(name):
    if name not in chatters:
        chatters[name] = Chatter(context, name)

def chatter_attack(attacker, victim, counter, attacker_faint, victim_faint):
    if attacker in chatters and victim in chatters:
        chatters[attacker].attack(chatters[victim], counter, attacker_faint, victim_faint)
        return True
    else:
        return False

def chatter_defend(defender, defended):
    if defender in chatters and defended in chatters:
        chatters[defender].defend(chatters[defended])
        return True
    else:
        return False

def chatter_heal(healer, healed):
    if healer in chatters and healed in chatters:
        chatters[healer].heal(chatters[healed])
        return True
    else:
        return False

def set_chatter_defended(chatter, defended):
    chatters[chatter].set_defended(defended)

if __name__ == "__main__":
    read_settings()
    load_sheets_from_folder()
    context["spritesheets"] = SpriteSheets

    # Interface the twitch thread communicates through
    set_funcs({
        "add_chatter": add_chatter,
        "chatter_attack": chatter_attack,
        "chatter_defend": chatter_defend,
        "chatter_heal": chatter_heal,
        "set_chatter_defended": set_chatter_defended,
        "set_last_command_time": set_last_command_time
    })

    twitch_thread = threading.Thread(target=start_twitch_handler_thread, args=[context])
    twitch_thread.start()

    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode(context["screen_size"])
    context["font"] = pygame.font.SysFont('Verdana', 16)

    chatters["zingochris"] = Chatter(context, "zingochris")
    bubble_img = pygame.image.load("bubble.png")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: break
        
        for chatter in chatters:
            if chatters[chatter].get_schedule() == "IDLE":
                chatters[chatter].set_schedule("WANDER")
            chatters[chatter].run_schedule()
        
        screen.fill(background)
        # Only render if there's been a command within the last RENDERING_TIMEOUT_SECONDS seconds
        if time.time() < LAST_COMMAND_TIME+RENDERING_TIMEOUT_SECONDS:
            for chatter in chatters:
                screen.blit(chatters[chatter].get_name_text(), (chatters[chatter].get_rect().centerx-(chatters[chatter].get_name_text().get_rect().width/2), chatters[chatter].get_rect().top - 20))
                screen.blit(pygame.transform.flip(chatters[chatter].get_img(), chatters[chatter].get_flip(), False), chatters[chatter].get_rect(), chatters[chatter].get_crop_square())
                if chatters[chatter].get_defended():
                    screen.blit(bubble_img, (chatters[chatter].get_rect().centerx-(bubble_img.get_rect().width/2), chatters[chatter].get_rect().centery-(bubble_img.get_rect().height/2)))
        pygame.display.flip()
        time.sleep(0.01)
    
    twitch_thread.join()
    sys.exit()