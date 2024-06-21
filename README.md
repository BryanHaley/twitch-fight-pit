# Twitch Fight Pit

Twitch overlay app allowing chatters to battle each other via chat commands.

## Usage

In `settings.json` specify `TWITCH_APP_ID` and `TWITCH_APP_SECRET`. Get these from registering an application on dev.twitch.tv. Set `TWITCH_CHANNEL` to the channel you want to run the bot in.

Ensure the executable has permissions to write to the folder it is located in. (The easiest way to do this is to place somewhere in your C:\Users\\<username\> directory).

Run `zingo-fight-pit.exe` on Windows, or on any platform `pip install -r requirements.txt` and `python zingo-fight-pit.py`

Add a window capture in OBS for the app.

Chatters can then send the following commands (customizable):
```
!attack : Attack another chatter
!defend : Give another chatter a shield that will reduce the next attack's damage by 50%.
!heal   : Heal another chatter
!pet    : Pet another chatter
!skin   : Change chatter's skin to an available skin
!skins  : List available skins
!lurk   : Remove chatter from fight pit
```

## Config

### settings.json

```
"TWITCH_APP_ID": Get from dev.twitch.tv.
"TWITCH_APP_SECRET": Get from dev.twitch.tv.
"TWITCH_CHANNEL": Set to desired channel.
"BACKGROUND_COLOR": List of three colors 0-255 representing red, green, and blue for the background color.
"RENDERING_TIMEOUT_SECONDS": If set, the app window will go blank if no one sends any recognized commands for this length of time.
"CHATTER_INACTIVITY_TIMEOUT": If set, the chatter will be removed from the fight pit if they haven't chatted for this length of time.
"COMMAND_TIMEOUT_SECONDS": If any chatter has sent a recognized command less than this length of time ago the subsequent command will be ignored.
"COMMAND_TIMEOUT_PER_USER": If a chatter has sent a recognized command less than this length of time ago the subsequent command from this chatter will be ignored.
"SCREEN_WIDTH": Horizontal size in pixels of game window.
"SCREEN_HEIGHT": Vertical size in pixels of game window.
"DEBUG": Enables debug routines.
"DEBUG_CHARACTERS": Adds test chatters for testing commands on. ("DEBUG" must be true).
"IGNORE_LIST": List of lowercase twitch handles to ignore.
"FLOOR_HEIGHT": Position in pixels from the top of the window for the floor. If not defined, it is set to the vertical center of the game window.
"SPRITE_MID_HEIGHT": The center of the sprite will be this amount of pixels above the floor.
"SPRITE_SPACING": Chatters will be this distance in pixels apart when interacting with each other.
"MOVE_CHANCE": Every frame while the chatter is standing still idling there is a 1 in MOVE_CHANCE chance they will start moving again.
"WALK_SPEED": Speed in pixels per second that chatters walk at.
"RUN_SPEED": Speed in pixels per second that chatters run at when approaching for an interaction.
"MOVE_EPSILON": Distance from the target a chatter can be to have "arrived". May need to be increased for very high walk or run speeds.
"FRAMERATE": Target frames per second for the app. 60 or a multiple of it is recommended.
"DEFAULT_HEALTH": Starting health of chatters.
"DAMAGE_RANGE": List of two numbers that defined the possible range of damage done with an attack.
"HEALING_RANGE": List of two numbers that defined the possible range of health points done with a healing.
"COUNTER_CHANCE": When attacked there is a 1 in COUNTER_CHANCE chance the chatter attacked will counter.
"NAMETAG_FONT": Name of system font for nametags.
"NAMETAG_FONT_SIZE": Font size for nametags.
"NAMETAG_COLOR": List of three colors 0-255 representing red, green, and blue for the nametag color.
"NAMETAG_ANTIALIAS": Apply anti-aliasing to nametags.
"NAMETAG_OVERLAP_LIMIT": How many nametags can stack on top of each other to avoid overlapping.
"INFO_CMD": chat command giving info about the fight pit bot.
"ATTACK_CMD": chat command to attack another chatter.
"ATTACK_PAST_TENSE": verbiage for the past tense of an attack.
"HEAL_CMD": chat command to heal another chatter.
"HEALED_PAST_TEST": verbiage for the past tense of a healing.
"DEFEND_CMD": chat command to defend another chatter.
"DEFEND_PAST_TENSE": verbiage for the past tense of a defense.
"PET_CMD": chat command to pet another chatter.
"PET_PAST_TENSE": verbiage for the past tense of a pet.
"SKIN_CMD": chat command to change the chatter's skin.
"SKINS_CMD": alias for the skin command; prints available skins when not given an argument.
"LURK_CMD": chat command to remove chatter from fight pit.
"CONNECT_EMOTE": emote used in connect message.
"FIGHT_EMOTE_1": first emote used in connect message.
"FIGHT_EMOTE_2": second emote used in connect message.
"ATTACK_EMOTE": emote used in attack message.
"DEFEND_EMOTE": emote used in defend message.
"HEAL_EMOTE": emote used in heal message.
"PET_EMOTE": emote used in pet message.
"FAINT_EMOTE": emote used in faint message.
"NOT_FOUND_EMOTE": emote used when targeted chatter is not found.
"FIGHT_PIT_NAME": Name of the fight pit used in the info command.
```

### skin_overrides.json

```
Entries of:
"twitch_handle": "skin_path"
For example:
{
  "aeomech": "skins/special/my_cool_skin",
  "zingochris": "skins/special/awesome_skin"
}
```

## Skins

Each skin gets a folder in either `skins/random` or `skins/special`. The folder name is the skin name.

Skins in the random folder are picked randomly for chatters with no set skin. They can also be selected with the `!skin` command.

If a skin in the `special` folder matches a chatter's name, that skin will automatically be applied to the chatter.

Other skins in the special folder can only be assigned to chatters by manually editing the `skin_overrides.json` file.

## Animating

Each skin needs the following animations:
```
attack
get-attacked
defend
get-defended
heal
get-healed
pet
get-pet
faint
walk
run
idle
```
Each animation gets one PNG spritesheet image in the skin folder.

The filename of the spritesheet determines several properties of the animation. Properties are split by underscores. The format is:
```
animation-name_framerate_looping_index.png

- animation-name: The name of the animation, corresponding to the list above.
- framerate: frames per second of the animation (usually 12)
- looping: "true" or "false" for if the animation loops endlessly. Walk, run, and idle should loop while the others should not.
- index: arbitrary number to differentiate variations of an animation. If multiple spritesheets exist for an animation, they will be chosen at random when the animation plays.

Examples:
attack_12_false_0.png
attack_12_false_1.png
faint_24_false_0.png
```

Within the spritesheet, your animation frames must be square; the number of frames in the animation is determined by how many multiples of the height the width is. That is to say, a 512x128 spritesheet will be determined to be four 128x128 frames.

Spritesheets do not need to be all the same size; for example `idle_12_true_0.png` can have 128x128 frames while `attack_12_false_0.png` can have 512x512 frames. The anchor point for each animation frame is the center of the frame, and the floor is assumed to be `SPRITE_MID_HEIGHT` (default: 64) pixels below the center of the frame.