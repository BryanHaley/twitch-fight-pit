import time
import random
import traceback
from twitch_interface import TwitchInterface
from game_interface import GameInterface
from settings import Settings
from skins import SkinOverrides
from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand

# Keep the available skins message under 500 characters
def split_skins_message(skins_list):
    msg_list = []
    current_msg = "Available skins: "
    for i, skin in enumerate(skins_list):
        if len(current_msg) + len(skin) + 4 >= 500:
            msg_list += [current_msg]
            current_msg = ""
        if i < len(skins_list)-1:
            current_msg += f"{skin}, "
        else:
            current_msg += f"{skin}"
    msg_list += [current_msg]
    return msg_list
    

# Callback for the chat connection being ready
async def on_ready(ready_event: EventData):
    try:
        print('Bot is ready for work; joining channel {}'.format(TwitchInterface.get_target_channel()))
        await ready_event.chat.join_room(TwitchInterface.get_target_channel())
        await ready_event.chat.send_message(TwitchInterface.get_target_channel(), f'Fight pit bot has connected to chat {Settings.connect_emote}')
    except:
        print(traceback.format_exc())

# Callback for messages in chat
async def on_message(msg: ChatMessage):
    try:
        if Settings.debug or str(msg.text).strip().startswith("!"):
            print(f'{msg.user.name}: {msg.text}')
        TwitchInterface.add_chatter(str(msg.user.name).lower())
    except:
        print("Failed to process chat message")
        print(traceback.format_exc())

# Function to handle typical commands
async def handle_command(cmd, commander, chatter, action, action_past_tense, emote, send_reply=True):
    try:
        # Add the commander chatter if he isn't there already
        TwitchInterface.add_chatter(commander)

        # Ignore command if commander is in ignore list or has recently sent a command
        if (commander in TwitchInterface.get_ignore_list() or
            time.time() < TwitchInterface.get_chatter_metadata()[commander]["last_command_time"]+Settings.command_timeout_per_user):
            print(f'{commander} is in ignore list or trying to send commands too quickly')
            return "FAILURE"
        
        # Ignore command if last command in general was too recent
        if time.time() < TwitchInterface.get_last_command_time()+Settings.command_timeout:
            print("Chatters are trying to send commands too quickly; ignoring")
            return "FAILURE"

        # Non-commanding user must already be in chatters for this to work
        if chatter not in TwitchInterface.get_chatter_metadata():
            await cmd.reply(f'{commander} tried to {action} {chatter}, but they were nowhere to be found! {Settings.not_found_emote}')
            return "FAILURE"
        
        # Queue the command
        GameInterface.enqueue_command({
            "action": action,
            "actor1": commander,
            "actor2": chatter,
            "metadata": None
        })

        # Tell the user it's happening
        if send_reply:
            await cmd.reply(f'{commander} {action_past_tense} {chatter}! {emote}')

        # Update last command time
        TwitchInterface.set_chatter_last_command_time(commander)

        return "SUCCESS"
    except:
        print("Failed to process {} command from {}".format(action, cmd.user.name))
        print(traceback.format_exc())

# Callback for the pet command
async def pet_command(cmd: ChatCommand):
    try:
        # Ignore zero length parameters
        if len(cmd.parameter) < 1:
            return "FAILURE"
        # Get actors
        commander = str(cmd.user.name).lower()
        chatter = str(cmd.parameter).lower()
        # Handle command
        await handle_command(cmd, commander, chatter, Settings.pet_cmd, Settings.pet_past_tense, Settings.pet_emote)
    except:
        print("Unknown error occurred handling pet command")
        print(traceback.format_exc())
        return "FAILURE"

# Callback for the squash command
async def attack_command(cmd: ChatCommand):
    try:
        # Ignore zero length parameters
        if len(cmd.parameter) < 1:
            return "FAILURE"
        # Get actors
        commander = str(cmd.user.name).lower()
        chatter = str(cmd.parameter).lower()
        # Handle command
        result = await handle_command(cmd, commander, chatter, Settings.attack_cmd, Settings.attack_past_tense, Settings.attack_emote, False)
        if result != "SUCCESS":
            return "FAILURE"
        # Determine damage and counter
        damage = random.randint(Settings.damage_range_min, Settings.damage_range_max)
        if GameInterface.is_actor_defended(chatter):
            damage = int(damage/2)
        counter_damage = random.randint(Settings.damage_range_min, Settings.damage_range_max)
        if GameInterface.is_actor_defended(commander):
            counter_damage = int(damage/2)
        counter = True if random.randint(1,Settings.counter_chance) == 1 else False
        # Apply damage
        chatter_status = TwitchInterface.damage_chatter(chatter, damage)
        if chatter_status == "FAINTED":
            counter = False # Can't counter if you've fainted
            GameInterface.enqueue_command({
                "action": "faint",
                "actor": chatter,
                "metadata": None
            })
        # If countering, queue that up
        if counter:
            GameInterface.enqueue_command({
                "action": Settings.attack_cmd,
                "actor1": chatter,
                "actor2": commander,
                "metadata": None
            })
        commander_status = "ALIVE"
        if counter:
            commander_status = TwitchInterface.damage_chatter(commander, counter_damage)
            if commander_status == "FAINTED":
                GameInterface.enqueue_command({
                    "action": "faint",
                    "actor": commander,
                    "metadata": None
                })
        # Build message
        msg = f'{commander} {Settings.attack_past_tense} {chatter} for {damage} damage!'
        if counter:
            msg += f' {chatter} counters for {counter_damage} damage!'
        msg += f' {Settings.attack_emote}'
        if chatter_status == "FAINTED":
            msg += f' {chatter} fainted! {Settings.faint_emote}'
        if commander_status == "FAINTED":
            msg += f' {commander} fainted! {Settings.faint_emote}'
        # Send message
        await cmd.reply(msg)
        return "SUCCESS"
    except:
        print("Unknown error occurred handling attack command")
        print(traceback.format_exc())
        return "FAILURE"

# Callback for the heal command
async def heal_command(cmd: ChatCommand):
    try:
        # Ignore zero length parameters
        if len(cmd.parameter) < 1:
            return "FAILURE"
        # Get actors
        commander = str(cmd.user.name).lower()
        chatter = str(cmd.parameter).lower()
        # Handle command
        await handle_command(cmd, commander, chatter, Settings.heal_cmd, Settings.healed_past_tense, Settings.heal_emote, False)
        # Calculate and apply healing value
        healing = random.randint(Settings.healing_range_min, Settings.healing_range_max)
        new_health = TwitchInterface.heal_chatter(chatter, healing)
        # Send reply
        await cmd.reply(f'{commander} {Settings.healed_past_tense} {chatter} for {healing} HP! They now have {new_health}/{Settings.default_health} HP! {Settings.heal_emote}')
        return "SUCCESS"
    except:
        print("Unknown error occurred handling heal command")
        print(traceback.format_exc())
        return "FAILURE"

# Callback for the defend command
async def defend_command(cmd: ChatCommand):
    try:
        # Ignore zero length parameters
        if len(cmd.parameter) < 1:
            return "FAILURE"
        # Get actors
        commander = str(cmd.user.name).lower()
        chatter = str(cmd.parameter).lower()
        # Handle command
        await handle_command(cmd, commander, chatter, Settings.defend_cmd, Settings.defend_past_tense, Settings.defend_emote)
        # Set defended status on chatter
        # GameInterface.defend_actor(chatter) # Set this during animation instead
        return "SUCCESS"
    except:
        print("Unknown error occurred handling defend command")
        print(traceback.format_exc())
        return "FAILURE"

# Callback for the skin command
async def skin_command(cmd: ChatCommand):
    try:
        # Get parameters
        commander = str(cmd.user.name).lower()
        skin = str(cmd.parameter).lower()
        # Add the commander chatter if he isn't there already
        TwitchInterface.add_chatter(commander)
        # Ignore command if commander is in ignore list or has recently sent a command
        if (commander in TwitchInterface.get_ignore_list() or
            time.time() < TwitchInterface.get_chatter_metadata()[commander]["last_command_time"]+Settings.command_timeout_per_user):
            print(f'{commander} is in ignore list or trying to send commands too quickly')
            return "FAILURE"
        # Ignore command if last command in general was too recent
        if time.time() < TwitchInterface.get_last_command_time()+Settings.command_timeout:
            print("Chatters are trying to send commands too quickly; ignoring")
            return "FAILURE"
        # Print available skins to chat if a skin wasn't specified
        if len(cmd.parameter) < 1:
            skins_msg = split_skins_message(SkinOverrides.get_available_skins())
            for msg in skins_msg:
                await cmd.reply(msg)
            return "SUCCESS"
        # Set skin override
        result = SkinOverrides.set_override(commander, skin)
        if result == "FAILURE":
            await cmd.reply(f'Selecting skin {skin} failed. Did you spell it correctly?')
            return "FAILURE"
        GameInterface.enqueue_command({
                "action": "update_skin",
                "actor": commander,
                "metadata": None
            })
        await cmd.reply(f'Updating skin for {commander} to {skin} {Settings.skin_update_emote}')
        TwitchInterface.set_chatter_last_command_time(commander)
        return "SUCCESS"
    except:
        print("Unknown error occurred handling skin command")
        print(traceback.format_exc())
        return "FAILURE"

# Callback for the lurk command
async def lurk_command(cmd: ChatCommand):
    try:
        # Courtesy command to delete a chatter when they lurk
        commander = str(cmd.user.name).lower()
        GameInterface.enqueue_delete_actor(commander)
        TwitchInterface.delete_chatter(commander)
        return "SUCCESS"
    except:
        print("Unknown error occurred handling lurk command")
        print(traceback.format_exc())
        return "FAILURE"

# Callback for the info command
async def info_command(cmd: ChatCommand):
    try:
        await cmd.reply(f'{Settings.fight_emote_1} {Settings.fight_emote_2} ' +
                        f'Participate in the {Settings.fight_pit_name}! Throw hands with each other using any of these commands: ' +
                        f'!{Settings.info_cmd}, ' +
                        f'!{Settings.attack_cmd}, ' +
                        f'!{Settings.defend_cmd}, ' +
                        f'!{Settings.heal_cmd}, ' +
                        f'!{Settings.pet_cmd}, ' +
                        f'!{Settings.skin_cmd}, ' +
                        f'!{Settings.skins_cmd}, ' +
                        f'!{Settings.lurk_cmd}')
        return "SUCCESS"
    except:
        print("Unknown error occurred handling lurk command")
        print(traceback.format_exc())
        return "FAILURE"

# this is where we set up the bot
async def run_twitch_handler():
    # Define twitch connection details
    twitch = await Twitch(TwitchInterface.get_app_id(), TwitchInterface.get_app_secret())
    user_scope = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]
    auth = UserAuthenticator(twitch, user_scope)
    token, refresh_token = await auth.authenticate() # TODO: Figure out if we have to do this every time
    await twitch.set_user_authentication(token, user_scope, refresh_token)

    # Create chat connection
    chat = await Chat(twitch)

    # Register event handlers
    chat.register_event(ChatEvent.READY, on_ready)
    chat.register_event(ChatEvent.MESSAGE, on_message)

    # Register command handlers
    chat.register_command(Settings.attack_cmd, attack_command)
    chat.register_command(Settings.defend_cmd, defend_command)
    chat.register_command(Settings.heal_cmd, heal_command)
    chat.register_command(Settings.pet_cmd, pet_command)
    chat.register_command(Settings.skin_cmd, skin_command)
    chat.register_command(Settings.skins_cmd, skin_command)
    chat.register_command(Settings.lurk_cmd, lurk_command)
    chat.register_command(Settings.info_cmd, info_command)

    # Start chat connection
    chat.start()

    while not TwitchInterface.want_quit():
        if TwitchInterface.want_quit():
            break
        # Check if we need to delete any chatters
        delete_queue = []
        for chatter in TwitchInterface.get_chatter_metadata():
            chatter_name = chatter
            chatter = TwitchInterface.get_chatter_metadata()[chatter]
            if (Settings.chatter_inactivity_timeout and 
                time.time() > chatter["last_chat_time"] + Settings.chatter_inactivity_timeout
                and chatter_name != TwitchInterface.get_target_channel()):
                GameInterface.enqueue_delete_actor(chatter_name)
                delete_queue += [chatter_name]
        for chatter in delete_queue:
            TwitchInterface.delete_chatter(chatter)
        time.sleep(0.1)
    
    chat.stop()
    await twitch.close()