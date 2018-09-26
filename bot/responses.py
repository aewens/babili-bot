import re
from datetime import datetime

class Responses:
    def __init__(self, bot):
        self.bot = bot
        self.triggers = {
            "name": dict(),
            "source": dict(),
            "response": dict()
        }

    def add_trigger(self, trigger_type, pattern, callback):
        if trigger_type in self.triggers:
            self.triggers[trigger_type][pattern] = callback

    def allowed(self, name, source):
        memories = self.bot.memories
        users = memories["users"]
        if name not in users:
            return False

        if name in users and "blacklist" in users[name]:
            reason = users[name]["blacklist"]["reason"]
            message = "is ignoring {} for reason '{}'".format(name, reason)
            self.bot.send_action(source, message)
            return False

        last_response =  0
        if "last_response" in self.bot.memories["users"][name]:
            last_response = self.bot.memories["users"][name]["last_response"]

        now = datetime.now().timestamp()
        author = self.bot.author
        wait = 1

        if name != author and last_response > 0 and now - last_response < wait:
            self.bot.memories["users"][name]["blacklist"] = {
                "reason": "Auto-banished",
                "when": now
            }
            return False

        return True

    def parse(self, name, source, response):
        users = self.bot.memories["users"]
        if name not in users:
            return False

        check = response.lower().strip()
        trig = {
            "name": name,
            "source": source,
            "response": response.lower().strip()
        }

        for trigger in list(self.triggers.keys()):
            for pattern, callback in self.triggers[trigger].items():
                if pattern[0] != "/" and pattern[-1] != "/":
                    if pattern == check and self.allowed(name, source):
                        callback(self, name, source, response)
                else:
                    regex = re.compile(pattern[1:-1])
                    if regex.match(trig[trigger]) is not None:
                        if self.allowed(name, source):
                            callback(self, name, source, response)

        now = datetime.now().timestamp()
        self.bot.memories["users"][name]["last_response"] = now