def botlist(self, name, source, response):
    name = self.bot.botnick
    author = self.bot.author
    email = self.bot.settings["email"]
    about = "the meta chat bot"
    commands = ", ".join([
        "!botlist",
        "!rollcall"
    ])
    args = (name, author, email, about, commands)
    message = "{} | {} <{}> | {} | {}".format(*args)
    self.bot.send_message(source, message)