import json
import sys
import pygame

class _Settings:
    def __init__(self):
        self._settings_json = None
        self._default_settings = {
            "TWITCH_APP_ID": None,
            "TWITCH_APP_SECRET": None,
            "TWITCH_CHANNEL": None,
            "BACKGROUND_COLOR": [0,177,64],
            "RENDERING_TIMEOUT_SECONDS": None,
            "CHATTER_INACTIVITY_TIMEOUT": None,
            "COMMAND_TIMEOUT_SECONDS": 0,
            "COMMAND_TIMEOUT_PER_USER": 0,
            "SCREEN_WIDTH": 800,
            "SCREEN_HEIGHT": 600,
            "DEBUG": False,
            "IGNORE_LIST": ["nightbot", "streamelements", "streamlabs", "moobot"],
            "FLOOR_HEIGHT": None,
            "SPRITE_MID_HEIGHT": 64,
            "SPRITE_SPACING": 64,
            "MOVE_CHANCE": 250,
            "WALK_SPEED": 40,
            "RUN_SPEED": 100,
            "MOVE_EPSILON": 2,
            "FRAMERATE": 60,
            "DEFAULT_HEALTH": 20000,
            "DAMAGE_RANGE": [99,9999],
            "HEALING_RANGE": [99,2999],
            "COUNTER_CHANCE": 10,
            "NAMETAG_FONT": "Verdana",
            "NAMETAG_FONT_SIZE": 16,
            "NAMETAG_COLOR": [0,0,0],
            "NAMETAG_ANTIALIAS": True,
            "NAMETAG_OVERLAP_LIMIT": 5
        }
    
    def init_from_file(self, filepath):
        # Parse json file
        with open(filepath, "r") as settings_file:
            self._settings_json = json.load(settings_file)
        
        # Copy default settings for any missing settings
        for item in self._default_settings:
            if item not in self._settings_json:
                self._settings_json[item] = self._default_settings[item]
        
        # Get twitch settings
        self.app_id = self._settings_json["TWITCH_APP_ID"]
        self.app_secret = self._settings_json["TWITCH_APP_SECRET"]
        self.target_channel = self._settings_json["TWITCH_CHANNEL"]

        # Sanity check
        if not self.app_id or not self.app_secret or not self.target_channel:
            print("Settings json malformed; check twitch connection details")
            sys.exit()

        # Get background color
        self.background_color = (
            max(0, min(255, self._settings_json["BACKGROUND_COLOR"][0])),
            max(0, min(255, self._settings_json["BACKGROUND_COLOR"][1])),
            max(0, min(255, self._settings_json["BACKGROUND_COLOR"][2]))
        )

        # Timeouts
        self.chatter_inactivity_timeout = max(30, self._settings_json["CHATTER_INACTIVITY_TIMEOUT"]) if self._settings_json["CHATTER_INACTIVITY_TIMEOUT"] else None
        self.rendering_timeout = max(30, self._settings_json["RENDERING_TIMEOUT_SECONDS"]) if self._settings_json["RENDERING_TIMEOUT_SECONDS"] else None
        self.command_timeout = max(0, self._settings_json["COMMAND_TIMEOUT_SECONDS"])
        self.command_timeout_per_user = max(0, self._settings_json["COMMAND_TIMEOUT_PER_USER"])
        self.screen_width = max(320, self._settings_json["SCREEN_WIDTH"])
        self.screen_height = max(240, self._settings_json["SCREEN_HEIGHT"])
        self.screen_size = (
            self.screen_width,
            self.screen_height
        )

        # Heights
        self.floor_height = self._settings_json["FLOOR_HEIGHT"]
        self.floor_height = self.floor_height if self.floor_height else self.screen_height/2
        self.sprite_mid_height = self._settings_json["SPRITE_MID_HEIGHT"]
        self.sprite_elevation = self.floor_height - self.sprite_mid_height

        # Misc
        self.debug = self._settings_json["DEBUG"]
        self.ignore_list = self._settings_json["IGNORE_LIST"]
        self.move_chance = self._settings_json["MOVE_CHANCE"]
        self.sprite_spacing = self._settings_json["SPRITE_SPACING"]
        self.walk_speed = self._settings_json["WALK_SPEED"]
        self.run_speed = self._settings_json["RUN_SPEED"]
        self.move_epsilon = max(0, self._settings_json["MOVE_EPSILON"])
        self.framerate = max(12, self._settings_json["FRAMERATE"])
        self.default_health = max(0, self._settings_json["DEFAULT_HEALTH"])
        self.damage_range_min = max(0, self._settings_json["DAMAGE_RANGE"][0])
        self.damage_range_max = max(1, self._settings_json["DAMAGE_RANGE"][1])
        self.healing_range_min = max(0, self._settings_json["HEALING_RANGE"][0])
        self.healing_range_max = max(1, self._settings_json["HEALING_RANGE"][1])
        self.counter_chance = max(1, self._settings_json["COUNTER_CHANCE"])
        self.nametag_font_size = max(6, self._settings_json["NAMETAG_FONT_SIZE"])
        self.nametag_font = pygame.font.SysFont(self._settings_json["NAMETAG_FONT"], self.nametag_font_size)
        self.nametag_color = (
            max(0, min(255, self._settings_json["NAMETAG_COLOR"][0])),
            max(0, min(255, self._settings_json["NAMETAG_COLOR"][1])),
            max(0, min(255, self._settings_json["NAMETAG_COLOR"][2]))
        )
        self.nametag_antialias = self._settings_json["NAMETAG_ANTIALIAS"]
        self.nametag_overlap_limit = max(1, self._settings_json["NAMETAG_OVERLAP_LIMIT"])

Settings = _Settings()