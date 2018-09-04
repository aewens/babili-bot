#!/usr/bin/env python3

from bot import Bot

bot = Bot("127.0.0.1", 6667, "BabiliBot|py", ["#bots"])

def processor(message):
    if "PRIVMSG" in message:
        name, source, response = parse(message)
        bot.send_message(source, "Got response")
    if "PING :" in message:
        ping(message)

if __name__ == "__main__":
    bot.start(processor, "settings.json")