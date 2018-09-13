def botlist(self, name, source, response):
    botnick = self.bot.botnick
    author = self.bot.author
    email = self.bot.settings["email"]
    about = "the meta chat bot"
    commands = ", ".join([
        "!botlist",
        "!rollcall",
        "!summon",
        "!banish",
        "!pardon"
    ])
    args = (botnick, author, email, about, commands)
    message = "{} | {} <{}> | {} | {}".format(*args)
    self.bot.send_message(source, message)