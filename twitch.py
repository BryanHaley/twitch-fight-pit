import time
import random
import traceback
from twitch_interface import TwitchInterface
from game_interface import GameInterface
from settings import Settings
from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand

# Callback for the chat connection being ready
async def on_ready(ready_event: EventData):
    print('Bot is ready for work, joining channels')
    await ready_event.chat.join_room(TwitchInterface.get_target_channel())

# Callback for messages in chat
async def on_message(msg: ChatMessage):
    try:
        if Settings.debug:
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
            await cmd.reply(f'{commander} tried to {action} {chatter}, but they were nowhere to be found! zingocConfused zingocConfused zingocConfused')
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
            await cmd.reply(f'{commander} {action_past_tense} {chatter}! {emote} {emote} {emote}')

        # Update last command time
        TwitchInterface.set_chatter_last_command_time(commander)

        return "SUCCESS"
    except:
        print("Failed to process {} command from {}".format(action, cmd.user.name))
        print(traceback.format_exc())

# Callback for the pet command
async def pet_command(cmd: ChatCommand):
    # Ignore zero length parameters
    if len(cmd.parameter) < 1:
        return "FAILURE"
    # Get actors
    commander = str(cmd.user.name).lower()
    chatter = str(cmd.parameter).lower()
    # Handle command
    await handle_command(cmd, commander, chatter, "pet", "pet", "Petthezingo")

# Callback for the squash command
async def attack_command(cmd: ChatCommand):
    # Ignore zero length parameters
    if len(cmd.parameter) < 1:
        return "FAILURE"
    # Get actors
    commander = str(cmd.user.name).lower()
    chatter = str(cmd.parameter).lower()
    # Handle command
    await handle_command(cmd, commander, chatter, "squash", "squashed", "zingo37Foot")

# Callback for the heal command
async def heal_command(cmd: ChatCommand):
    # Ignore zero length parameters
    if len(cmd.parameter) < 1:
        return "FAILURE"
    # Get actors
    commander = str(cmd.user.name).lower()
    chatter = str(cmd.parameter).lower()
    # Handle command
    await handle_command(cmd, commander, chatter, "heal", "healed", "zingoW")

# Callback for the defend command
async def defend_command(cmd: ChatCommand):
    # Ignore zero length parameters
    if len(cmd.parameter) < 1:
        return "FAILURE"
    # Get actors
    commander = str(cmd.user.name).lower()
    chatter = str(cmd.parameter).lower()
    # Handle command
    await handle_command(cmd, commander, chatter, "defend", "defended", "zingocCool")


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
    chat.register_command('squash', attack_command)
    chat.register_command('defend', defend_command)
    chat.register_command('heal', heal_command)
    chat.register_command('pet', pet_command)

    # Start chat connection
    chat.start()

    while not TwitchInterface.want_quit():
        if TwitchInterface.want_quit():
            break
        time.sleep(0.1)
    
    chat.stop()
    await twitch.close()