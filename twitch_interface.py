import time
import random
from game_interface import GameInterface

class _TwitchInterface:
    def __init__(self):
        self._chatter_metadata = {}
        self._ignore_list = []
        self._app_id = ""
        self._app_secret = ""
        self._target_channel = ""
        self._want_quit = False
    
    # This actually gets called every time a chatter chats
    def add_chatter(self, name):
        if name in self._ignore_list:
            return
        if name not in self._chatter_metadata:
            self._chatter_metadata[name] = {
                "last_chat_time": 0
            }
        self.set_chatter_last_chat_time(name)
        GameInterface.add_actor(name, random.randint(100,700))
    
    def set_chatter_last_chat_time(self, name):
        if name in self._ignore_list or name not in self._chatter_metadata:
            return
        self._chatter_metadata[name]["last_chat_time"] = time.time()
    
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

TwitchInterface = _TwitchInterface()