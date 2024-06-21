import time
import random
import traceback
from game_interface import GameInterface

class _TwitchInterface:
    def __init__(self):
        self._chatter_metadata = {}
        self._ignore_list = []
        self._app_id = ""
        self._app_secret = ""
        self._target_channel = ""
        self._chatter_default_health = 20000
        self._last_command_time = time.time()
        self._want_quit = False
    
    # This actually gets called every time a chatter chats
    def add_chatter(self, name):
        if name in self._ignore_list:
            return
        if name not in self._chatter_metadata:
            self._chatter_metadata[name] = {
                "last_chat_time": 0,
                "last_command_time": 0,
                "health": self._chatter_default_health
            }
        self.set_chatter_last_chat_time(name)
        self.set_chatter_last_command_time(name)
        GameInterface.add_actor(name, random.randint(100,700))
    
    def update_last_command_time(self):
        self._last_command_time = time.time()

    def damage_chatter(self, name, damage):
        self._chatter_metadata[name]["health"] -= damage
        GameInterface.undefend_actor(name)
        if self._chatter_metadata[name]["health"] <= 0:
            self._chatter_metadata[name]["health"] = self._chatter_default_health
            return "FAINTED"
        return "ALIVE"
    
    def heal_chatter(self, name, healing):
        self._chatter_metadata[name]["health"] += healing
        if self._chatter_metadata[name]["health"] > self._chatter_default_health:
            self._chatter_metadata[name]["health"] = self._chatter_default_health
        return self._chatter_metadata[name]["health"]
    
    def set_chatter_default_health(self, health):
        self._chatter_default_health = health
    
    def set_chatter_last_chat_time(self, name):
        if name in self._ignore_list or name not in self._chatter_metadata:
            return
        self._chatter_metadata[name]["last_chat_time"] = time.time()
    
    def set_chatter_last_command_time(self, name):
        if name in self._ignore_list or name not in self._chatter_metadata:
            return
        self._chatter_metadata[name]["last_command_time"] = time.time()
        self.update_last_command_time()
    
    def delete_chatter(self, name):
        try:
            if name not in self._chatter_metadata:
                return "SUCCESS"
            del self._chatter_metadata[name]
            return "SUCCESS"
        except:
            print("Failed to delete chatter {}".format(name))
            print(traceback.format_exc())
            return "FAILURE"
    
    def set_app_id(self, app_id):
        self._app_id = app_id
    
    def set_app_secret(self, app_secret):
        self._app_secret = app_secret
    
    def set_target_channel(self, target_channel):
        self._target_channel = target_channel
    
    def set_ignore_list(self, ignore_list):
        self._ignore_list = ignore_list
    
    def quit(self):
        self._want_quit = True

    def want_quit(self):
        return self._want_quit
    
    def get_chatter_metadata(self):
        return self._chatter_metadata

    def get_app_id(self):
        return self._app_id
    
    def get_app_secret(self):
        return self._app_secret
    
    def get_target_channel(self):
        return self._target_channel
    
    def get_ignore_list(self):
        return self._ignore_list

    def get_last_command_time(self):
        return self._last_command_time

TwitchInterface = _TwitchInterface()