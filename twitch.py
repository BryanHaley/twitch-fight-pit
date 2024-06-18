import time
import random
from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand

APP_ID = None
APP_SECRET = None
USER_SCOPE = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]
TARGET_CHANNEL = None
BOT_READY = False
COMMAND_TIMEOUT_SECONDS = 5
LAST_COMMAND_TIME = time.time()

context = {}
main_funcs = {}
chatters = {}

def set_funcs(funcs):
    main_funcs["add_chatter"] = funcs["add_chatter"]
    main_funcs["chatter_attack"] = funcs["chatter_attack"]
    main_funcs["chatter_defend"] = funcs["chatter_defend"]
    main_funcs["chatter_heal"] = funcs["chatter_heal"]
    main_funcs["chatter_pet"] = funcs["chatter_pet"]
    main_funcs["set_chatter_defended"] = funcs["set_chatter_defended"]
    main_funcs["set_last_command_time"] = funcs["set_last_command_time"]
    main_funcs["get_want_quit"] = funcs["get_want_quit"]

# this will be called when the event READY is triggered, which will be on bot start
async def on_ready(ready_event: EventData):
    print('Bot is ready for work, joining channels')
    # join our target channel, if you want to join multiple, either call join for each individually
    # or even better pass a list of channels as the argument
    await ready_event.chat.join_room(TARGET_CHANNEL)
    # you can do other bot initialization things in here
    BOT_READY = True


# this will be called whenever a message in a channel was send by either the bot OR another user
async def on_message(msg: ChatMessage):
    print(f'in {msg.room.name}, {msg.user.name} said: {msg.text}')
    if msg.user.name not in chatters:
        main_funcs["add_chatter"](msg.user.name)
        chatters[msg.user.name] = {"health": 20000, "defended": False}


# this will be called whenever someone subscribes to a channel
async def on_sub(sub: ChatSub):
    print(f'New subscription in {sub.room.name}:\\n'
          f'  Type: {sub.sub_plan}\\n'
          f'  Message: {sub.sub_message}')

async def attack_command(cmd: ChatCommand):
    # Don't respond if the timeout hasn't elapsed
    global LAST_COMMAND_TIME
    global COMMAND_TIMEOUT_SECONDS
    if time.time() < LAST_COMMAND_TIME+COMMAND_TIMEOUT_SECONDS:
        return
    LAST_COMMAND_TIME = time.time()
    main_funcs["set_last_command_time"](time.time())
    if cmd.parameter.startswith('@'):
        cmd.parameter = cmd.parameter[1:]
    
    if len(cmd.parameter) == 0:
        await cmd.reply(f"{cmd.user.name} squashed a zingo! zingo37Foot zingo37Foot zingo37Foot")
    elif cmd.user.name == cmd.parameter:
        pass # Ignore commands on self
    else:
        if cmd.user.name not in chatters:
            main_funcs["add_chatter"](cmd.user.name)
            chatters[cmd.user.name] = {"health": 20000, "defended": False}
        if cmd.parameter not in chatters:
            await cmd.reply(f'{cmd.user.name} tried to squash {cmd.parameter}, but they were nowhere to be found! zingocConfused zingocConfused zingocConfused')
            return
            
        damage = random.randint(100,9999)
        if chatters[cmd.parameter]["defended"]:
            damage = int(damage/2)
        counter_damage = random.randint(100,9999)
        if chatters[cmd.user.name]["defended"]:
            counter_damage = int(damage/2)
        counter = True if random.randint(0,3) == 0 else False
        attacker_faint = False
        victim_faint = False
        if cmd.user.name in chatters and chatters[cmd.user.name]["health"]-counter_damage < 0 and counter:
            attacker_faint = True
        if cmd.parameter in chatters and chatters[cmd.parameter]["health"]-damage < 0:
            victim_faint = True
        
        if main_funcs["chatter_attack"](cmd.user.name, cmd.parameter, counter, attacker_faint, victim_faint):
            if not counter:
                await cmd.reply(f'{cmd.user.name} squashed {cmd.parameter} for {damage} damage! zingo37Foot zingo37Foot zingo37Foot')
                chatters[cmd.parameter]["health"] -= damage
                chatters[cmd.parameter]["defended"] = False
                # main_funcs["set_chatter_defended"](cmd.parameter, False) # Let this be set by animation
            else:
                await cmd.reply(f'{cmd.user.name} squashed {cmd.parameter} for {damage} damage! {cmd.parameter} counters for {counter_damage} damage! zingo37Foot zingo37Foot zingo37Foot')
                chatters[cmd.parameter]["health"] -= damage
                chatters[cmd.parameter]["defended"] = False
                # main_funcs["set_chatter_defended"](cmd.parameter, False) # Let this be set by animation
                chatters[cmd.user.name]["health"] -= counter_damage
                chatters[cmd.user.name]["defended"] = False
                main_funcs["set_chatter_defended"](cmd.user.name, False)
            
            if cmd.user.name in chatters and chatters[cmd.user.name]["health"] < 0:
                await cmd.reply(f'{cmd.user.name} fainted! zingocSad')
                chatters[cmd.user.name] = 20000
            if cmd.parameter in chatters and chatters[cmd.parameter]["health"] < 0:
                await cmd.reply(f'{cmd.parameter} fainted! zingocSad')
                chatters[cmd.parameter] = 20000
        else:
            await cmd.reply(f'{cmd.user.name} tried to squash {cmd.parameter}, but they failed! zingocConfused zingocConfused zingocConfused')

async def defend_command(cmd: ChatCommand):
    # Don't respond if the timeout hasn't elapsed
    global LAST_COMMAND_TIME
    global COMMAND_TIMEOUT_SECONDS
    if time.time() < LAST_COMMAND_TIME+COMMAND_TIMEOUT_SECONDS:
        return
    LAST_COMMAND_TIME = time.time()
    main_funcs["set_last_command_time"](time.time())
    if cmd.parameter.startswith('@'):
        cmd.parameter = cmd.parameter[1:]
    
    if len(cmd.parameter) == 0:
        await cmd.reply(f"{cmd.user.name} defended a zingo! zingoW")
    elif cmd.user.name == cmd.parameter:
        pass # Ignore commands on self
    else:
        if cmd.user.name not in chatters:
            main_funcs["add_chatter"](cmd.user.name)
            chatters[cmd.user.name] = {"health": 20000, "defended": False}
        if cmd.parameter not in chatters:
            await cmd.reply(f'{cmd.user.name} tried to defend {cmd.parameter}, but they were nowhere to be found! zingocConfused zingocConfused zingocConfused')
            return

        success = True if random.randint(0,3) != 0 else False

        if not success:
            await cmd.reply(f'{cmd.user.name} tried to defend {cmd.parameter}, but they failed! zingocSad')
            return
        
        if main_funcs["chatter_defend"](cmd.user.name, cmd.parameter):
            await cmd.reply(f'{cmd.user.name} defended {cmd.parameter}! zingoW')
            # main_funcs["set_chatter_defended"](cmd.parameter, True) # Let this be set by animation
            chatters[cmd.parameter]["defended"] = True
        else:
            await cmd.reply(f'{cmd.user.name} tried to defend {cmd.parameter}, but they failed! zingocConfused zingocConfused zingocConfused')

async def heal_command(cmd: ChatCommand):
    # Don't respond if the timeout hasn't elapsed
    global LAST_COMMAND_TIME
    global COMMAND_TIMEOUT_SECONDS
    if time.time() < LAST_COMMAND_TIME+COMMAND_TIMEOUT_SECONDS:
        return
    LAST_COMMAND_TIME = time.time()
    main_funcs["set_last_command_time"](time.time())
    if cmd.parameter.startswith('@'):
        cmd.parameter = cmd.parameter[1:]
    
    if len(cmd.parameter) == 0:
        await cmd.reply(f"{cmd.user.name} healed a zingo! Petthezingo")
    elif cmd.user.name == cmd.parameter:
        pass # Ignore commands on self
    else:
        if cmd.user.name not in chatters:
            main_funcs["add_chatter"](cmd.user.name)
            chatters[cmd.user.name] = {"health": 20000, "defended": False}
        if cmd.parameter not in chatters:
            await cmd.reply(f'{cmd.user.name} tried to heal {cmd.parameter}, but they were nowhere to be found! zingocConfused zingocConfused zingocConfused')
            return

        success = True if random.randint(0,2) != 0 else False

        if not success:
            await cmd.reply(f'{cmd.user.name} tried to heal {cmd.parameter}, but they failed! zingocSad')
            return
        
        if main_funcs["chatter_heal"](cmd.user.name, cmd.parameter):
            chatters[cmd.parameter]["health"] += 2000
            if chatters[cmd.parameter]["health"] > 20000:
                chatters[cmd.parameter]["health"] = 20000
            await cmd.reply(f'{cmd.user.name} healed {cmd.parameter}! Petthezingo They now have {chatters[cmd.parameter]["health"]}/20000 health points.')
        else:
            await cmd.reply(f'{cmd.user.name} tried to heal {cmd.parameter}, but they failed! zingocConfused zingocConfused zingocConfused')

async def pet_command(cmd: ChatCommand):
    # Don't respond if the timeout hasn't elapsed
    global LAST_COMMAND_TIME
    global COMMAND_TIMEOUT_SECONDS
    if time.time() < LAST_COMMAND_TIME+COMMAND_TIMEOUT_SECONDS:
        return
    LAST_COMMAND_TIME = time.time()
    main_funcs["set_last_command_time"](time.time())
    if cmd.parameter.startswith('@'):
        cmd.parameter = cmd.parameter[1:]
    
    if len(cmd.parameter) == 0:
        await cmd.reply(f"{cmd.user.name} pet a zingo! Petthezingo")
    elif cmd.user.name == cmd.parameter:
        pass # Ignore commands on self
    else:
        if cmd.user.name not in chatters:
            main_funcs["add_chatter"](cmd.user.name)
            chatters[cmd.user.name] = {"health": 20000, "defended": False}
        if cmd.parameter not in chatters:
            await cmd.reply(f'{cmd.user.name} tried to pet {cmd.parameter}, but they were nowhere to be found! zingocConfused zingocConfused zingocConfused')
            return
        
        if main_funcs["chatter_pet"](cmd.user.name, cmd.parameter):
            await cmd.reply(f'{cmd.user.name} pet {cmd.parameter}! Petthezingo Petthezingo Petthezingo')
        else:
            await cmd.reply(f'{cmd.user.name} tried to pet {cmd.parameter}, but they failed! zingocConfused zingocConfused zingocConfused')


# this is where we set up the bot
async def run_twitch_handler(main_context):
    # Set state
    # It would've been cleaner to just reference context but whatever, lazy
    global context
    global APP_ID
    global APP_SECRET
    global TARGET_CHANNEL
    global COMMAND_TIMEOUT_SECONDS
    global BOT_READY

    context = main_context
    APP_ID = context["TWITCH_APP_ID"]
    APP_SECRET = context["TWITCH_APP_SECRET"]
    TARGET_CHANNEL = context["TWITCH_CHANNEL"]
    COMMAND_TIMEOUT_SECONDS = context["COMMAND_TIMEOUT_SECONDS"]

    if context["DEBUG"]:
        chatters["testma"] = {
            "health": 20000,
            "defended": False
        }
    else:
        chatters[context["TWITCH_CHANNEL"]] = {
            "health": 20000,
            "defended": False
        }

    # set up twitch api instance and add user authentication with some scopes
    twitch = await Twitch(APP_ID, APP_SECRET)
    auth = UserAuthenticator(twitch, USER_SCOPE)
    token, refresh_token = await auth.authenticate()
    await twitch.set_user_authentication(token, USER_SCOPE, refresh_token)

    # create chat instance
    chat = await Chat(twitch)

    # register the handlers for the events you want

    # listen to when the bot is done starting up and ready to join channels
    chat.register_event(ChatEvent.READY, on_ready)
    # listen to chat messages
    chat.register_event(ChatEvent.MESSAGE, on_message)
    # listen to channel subscriptions
    chat.register_event(ChatEvent.SUB, on_sub)
    # there are more events, you can view them all in this documentation

    # you can directly register commands and their handlers, this will register the !reply command
    # chat.register_command('reply', test_command)
    chat.register_command('squash', attack_command)
    chat.register_command('defend', defend_command)
    chat.register_command('heal', heal_command)
    chat.register_command('pet', pet_command)

    # we are done with our setup, lets start this bot up!
    chat.start()

    while not BOT_READY:
        if main_funcs["get_want_quit"]():
            break
        time.sleep(0.1)

    while not main_funcs["get_want_quit"]():
        if main_funcs["get_want_quit"]():
            break
        time.sleep(0.1)
    
    chat.stop()
    await twitch.close()