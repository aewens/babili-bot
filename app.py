#!/usr/bin/env python3

from bot import Bot

bot = Bot("127.0.0.1", 6667, "BabiliBot|py", ["#bots"])

def processor(name, source, response):
    #bot.send_message(source, "Got response")
    print(name, source, response)

if __name__ == "__main__":
    bot.start(processor, "settings.json")