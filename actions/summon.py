from subprocess import Popen, PIPE
from email.mime.text import MIMEText

def summon(self, name, source, response):
    botnick = self.bot.botnick
    author = self.bot.author
    user, reason = response.split("!summon ")[1].split(" ", 1)

    email = "{}@tilde.team"

    message = MIMEText(" ".join([
        "My bot, {}, received a summoning request for you".format(botnick),
        "from {} in channel {} for reason: {}".format(name, source, reason)
    ]))

    message["From"] = email.format(botnick)
    message["To"] = email.format(user)
    message["Subject"] = "You have been summoned!"

    command = "/usr/sbin/sendmail -t -oi".split(" ")
    p = Popen(command, stdin=PIPE, universal_newlines=True)
    p.communicate(message.as_string())
    
    confirmation = "{}: You have summoned {}".format(name, user)
    self.bot.send_message(source, confirmation)