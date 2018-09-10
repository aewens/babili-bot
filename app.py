#!/usr/bin/env python3

from bot import Bot

bot = Bot("127.0.0.1", 6667, "BabiliBot|py", ["#bots"])

def handle_pm(name, response):
    print("PM: {} - {}".format(name, response))

def handle_message(name, source, response):
    #bot.send_message(source, "Got response")
    print("MSG: {} {} - {}".format(name, source, response))

def handle_mode(channel, mode):
    if mode == "-r":
        bot.send_message("ChanServ", "REGISTER {}", channel)
        bot.send_message("ChanServ", "SET Successor {} {}", chan, bot.botnick)
        bot.send_message("ChanServ", "SET Founder {} {}", chan, bot.author)

if __name__ == "__main__":
    bot.start("settings.json", {
        "pm": handle_pm,
        "message": handle_message,
        "mode": handle_mode
    })