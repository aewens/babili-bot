def puppet(self, name, source, response):
    botnick = self.bot.botnick
    author = self.bot.author
    command = response.split("!puppet ")[1]
    mode, place, message = command.split(" ", 2)

    if name != author:
        return

    modes = {
        "say": self.bot.send_message,
        "act": self.bot.send_action
    }
    default = lambda _, msg: self.bot.send_message(source, "Invalid action!")
    modes.get(mode, default)(place, message)

def inject(self, name, source, response):
    botnick = self.bot.botnick
    author = self.bot.author
    command = response.split("!inject ")[1]

    if name != author:
        return

    self.bot.send(command)

def nomad(self, name, source, response):
    botnick = self.bot.botnick
    author = self.bot.author
    command = response.split("!nomad ")[1]
    action, place = command.split(" ", 1)

    if name != author:
        return

    actions = {
        "join": self.bot.join,
        "leave": self.bot.leave
    }
    default = lambda p: self.bot.send_message(source, "Invalid action!")
    actions.get(action, default)(place)