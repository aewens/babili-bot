#!/usr/bin/env python3

from os.path import dirname, realpath

from bot import Bot, Tasks, Responses
from actions import actions
from coroutines import coroutines

debug = False
kingme = [] if debug else ["#chaos"]
channels = ["#bots", "#insane"] 
if not debug:
    channels.extend([
        "#meta",
        "#team",
        "#chaos",
        "#tildeverse"
    ])

bot = Bot("127.0.0.1", 6667, "BabiliBot", channels)
responses = Responses(bot)
tasks = Tasks(bot)

for action in actions:
    if "type" in action and "pattern" in action and "callback" in action:
        responses.add_trigger(
            action["type"], 
            action["pattern"], 
            action["callback"]
        )

# for coro in coroutines:
#     worker = coro["worker"]
#     interval = coro["interval"]
#     state = coro.get("state", None)
#     coro_state = state if state is not None else (bot,)
#     tasks.add_coroutine(worker, interval, coro_state)
tasks.coroutines = coroutines

def try_to_king_me(channel):
    bot.send_message("ChanServ", "REGISTER {}", channel)
    bot.send_message("ChanServ", "SET Successor {} {}", channel, bot.botnick)
    bot.send_message("ChanServ", "SET Founder {} {}", channel, bot.author)

def handle_pm(name, response):
    print("PM: {} - {}".format(name, response))

def handle_mode(channel, mode):
    if mode == "-r":
        try_to_king_me(channel)

def handle_invite(channel, name):
    if channel in kingme:
        try_to_king_me(channel)

    users = bot.memories["users"]
    if name not in users:
        bot.memories["users"][name] = dict()

    if "invites" not in users[name]:
        bot.memories["users"][name]["invites"] = list()

    bot.memories["users"][name]["invites"].append(channel)

def handle_kick(name):
    users = bot.memories["users"]
    if name not in users:
        bot.memories["users"][name] = dict()

    bot.memories["users"][name]["kicker"] = True

def handle_message(name, source, response):
    responses.parse(name, source, response)
    if response == "!debug":
        print("::", bot.memories)

if __name__ == "__main__":
    bot.tasks = tasks
    bot.start(dirname(realpath(__file__)), {
        "pm": handle_pm,
        "mode": handle_mode,
        "invite": handle_invite,
        "kick": handle_kick,
        "message": handle_message
    })