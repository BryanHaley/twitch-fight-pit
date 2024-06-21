import os
import json
import traceback

class _SkinOverrides:
    def __init__(self, path):
        self._overrides = {}
        self._overrides_filepath = path
        # Load overrides from file if it exists
        try:
            if os.path.exists(self._overrides_filepath):
                with open(self._overrides_filepath, "r") as overrides_file:
                    self._overrides = json.load(overrides_file)
        except:
            print("WARNING: Failed to load skin overrides from {}".format(path))
            print(traceback.format_exc())
    
    def get_available_skins(self):
        random_skins_path = os.path.join("skins", "random")
        return list(filter(lambda x: not os.path.isfile(x), os.listdir(random_skins_path)))
    
    def get_override_for_name(self, name):
        if name in self._overrides:
            return self._overrides[name]
        return None
    
    def set_override(self, name, skin):
        # Check if skin exists
        skin_path = os.path.join("skins", "random", "default")
        if name == skin:
            skin_path = os.path.join("skins", "special", skin)
            if not os.path.exists(skin_path) or os.path.isfile(skin_path):
                return "FAILURE"
        else:
            skin_path = os.path.join("skins", "random", skin)
            if not os.path.exists(skin_path) or os.path.isfile(skin_path):
                return "FAILURE"
        # Set override
        self._overrides[name] = skin_path
        # Dump overrides to file
        try:
            with open(self._overrides_filepath, "w+") as overrides_file:
                json.dump(self._overrides, overrides_file, indent=2)
        except:
            print("WARNING: Failed to save skin overrides to {}".format(self._overrides_filepath))
            print(traceback.format_exc())
        return "SUCCESS"

SkinOverrides = _SkinOverrides("skin_overrides.json")