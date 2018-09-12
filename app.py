#!/usr/bin/env python3

from bot import Bot, Tasks, Responses
from actions import actions

kickers = list()
inviters = dict()
kingme = [
    "#chaos"
]

bot = Bot("127.0.0.1", 6667, "BabiliBot|py", ["#bots"])
responses = Responses(bot)

for action in actions:
    if "type" in action and "pattern" in action and "callback" in action:
        responses.add_trigger(
            action["type"], 
            action["pattern"], 
            action["callback"]
        )

def try_to_king_me(bot, channel):
    bot.send_message("ChanServ", "REGISTER {}", channel)
    bot.send_message("ChanServ", "SET Successor {} {}", channel, bot.botnick)
    bot.send_message("ChanServ", "SET Founder {} {}", channel, bot.author)

def handle_pm(name, response):
    print("PM: {} - {}".format(name, response))

def handle_mode(channel, mode):
    if mode == "-r":
        try_to_king_me(bot, channel)

def handle_invite(channel, name):
    if channel in kingme:
        try_to_king_me(bot, channel)

    invites.append({
        "channel": channel,
        "name": name
    })

def handle_kick(kicker):
    kickers.append(kicker)

def handle_message(name, source, response):
    print("MSG: {} {} - {}".format(name, source, response))
    responses.parse(name, source, response)

if __name__ == "__main__":
    bot.start("settings.json", {
        "pm": handle_pm,
        "mode": handle_mode,
        "invite": handle_invite,
        "kick": handle_kick,
        "message": handle_message
    })