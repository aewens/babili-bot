#!/usr/bin/env python3

from os.path import dirname, realpath

from bot import Bot, Tasks, Responses
from actions import actions

kingme = [
    "#chaos"
]

bot = Bot("127.0.0.1", 6667, "BabiliBot|py", [
    "#bots",
    "#insane"
])
responses = Responses(bot)

for action in actions:
    if "type" in action and "pattern" in action and "callback" in action:
        responses.add_trigger(
            action["type"], 
            action["pattern"], 
            action["callback"]
        )

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
    bot.start(dirname(realpath(__file__)), {
        "pm": handle_pm,
        "mode": handle_mode,
        "invite": handle_invite,
        "kick": handle_kick,
        "message": handle_message
    })