from datetime import datetime

def banish(self, name, source, response):
    botnick = self.bot.botnick
    author = self.bot.author
    user, reason = response.split("!banish ")[1].split(" ", 1)

    if name != author:
        return

    if user not in self.bot.memories["users"]:
        self.bot.memories["users"][user] = dict()

    self.bot.memories["users"][user]["blacklist"] = {
        "reason": reason,
        "when": datetime.now().timestamp()
    }

    self.bot.save_memories()

    confirmation = "{} has been banished for reason: {}".format(user, reason)
    self.bot.send_message(source, confirmation)

def pardon(self, name, source, response):
    botnick = self.bot.botnick
    author = self.bot.author
    user = response.split("!pardon ")[1]

    if name != author:
        return

    del self.bot.memories["users"][user]["blacklist"]

    self.bot.save_memories()

    confirmation = "{} has been pardoned".format(user)
    self.bot.send_message(source, confirmation)