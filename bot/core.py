import re
import json
import socket

class Bot:
    def __init__(self, server, port, botnick, channels):
        self.ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = server
        self.port = port
        self.botnick = botnick
        self.channels = channels
        self.running = True
        
        self.users = dict()
        self.kickers = list()
        self.invites = list()

        self.author = ""
        self.kingme = []

        self.recv_size = 2048
        self.splitter = "\n\r"

    def send(self, message, *args):
        response = message.format(*args) + "\n"
        print("DEBUG: ", response)
        self.ircsock.send(response.encode())

    def send_message(self, target, message, *args):
        msg = message.format(*args)
        response = "PRIVMSG {0} :{1}".format(target, msg) + "\n"
        print("DEBUG: ", response)
        self.ircsock.send(response.encode())

    def join(self, chan):
        self.send("JOIN {}", chan)

        message = ""
        magic_string = "End of /NAMES list."
        while magic_string not in message:
            message = self.ircsock.recv(self.recv_size).decode()
            message = message.strip(self.splitter)
            print(message)

        if chan in self.kingme:
            self.try_to_king_me(chan)

        user_list = "= {} :".format(chan)
        raw_users = message.split(user_list)[1].split(" \r\n")[0].split(" ")
        prefix_filter = lambda u: u[1:] if "~" in u or "@" in u else u
        users = list(filter(prefix_filter, raw_users))
        for user in users:
            if user not in self.users:
                self.users[user] = dict()

    def ping(self, message):
        response = message.split("PING :")[1]
        self.send("PONG :{0}", response)

    def get_name(self, text):
        return text.split("!", 1)[0][1:]

    def parse(self, message):
        before, after = message.split("PRIVMSG ", 1)
        name = self.get_name(before)
        source, response = after.split(" :", 1)
        return name, source, response

    def handle_mode(self, message):
        before, after = message.split("MODE ", 1)
        name = self.get_name(before)
        channel, mode = after.split(" ")[:2]
        return channel, mode

    def handle_rename(self, message):
        before, new_name = message.split("NICK ", 1)
        name = self.get_name(before)
        user = self.users[name]
        del self.users[name]
        self.users[new_name] = user
        return user, new_name

    def handle_invite(self, message):
        before, after = message.split("INVITE ", 1)
        name = self.get_name(before)
        channel = after.split(":", 1)[1]
        self.join(channel)
        self.invites.append({
            "name": name,
            "channel": channel
        })
        return channel, name

    def handle_kick(self, message):
        regex = "KICK #\S+ {} :".format(self.botnick)
        before, kicker = re.split(regex, message)
        self.kickers.append(kicker)
        return kicker

    def try_to_king_me(self, chan):
        self.send_message("ChanServ", "REGISTER {}", chan)
        self.send_message("ChanServ", "SET Successor {} {}", chan, self.botnick)
        self.send_message("ChanServ", "SET Founder {} {}", chan, self.author)

    def load_settings(self, location):
        with open(location, "r") as f:
            self.settings = json.loads(f.read())

        set_vars = [
            "author",
            "kingme"
        ]

        for name, attr in self.settings.items():
            if name in set_vars:
                setattr(self, name, attr)

    def stop(self):
        self.running = False
        self.send("QUIT")

    def start(self, settings, callback):
        message = ""
        registered = False
        confirmed = True

        self.ircsock.connect((self.server, self.port))
        self.send("USER {0} {0} {0} {0}", self.botnick)
        self.send("NICK {0}", self.botnick)

        self.load_settings(settings)

        password = self.settings["password"] or ""
        confirm = self.settings["confirm"] or ""
        email = self.settings["email"] or ""

        magic_phrase = {
            "has_registered": "Password",
            "needs_to_register": "choose a different nick",
            "needs_to_confirm": "Your account will expire"
        }

        magic_string = "MODE {} +r".format(self.botnick)
        while magic_string not in message:
            message = self.ircsock.recv(self.recv_size).decode()
            message = message.strip(self.splitter)
            print(message)
            if not registered and magic_phrase["has_registered"] in message:
                registered = True
            if not registered and magic_phrase["needs_to_register"] in message:
                self.send_message("NickServ", "IDENTIFY {}", password)
            if not confirmed and magic_phrase["needs_to_confirm"] in message:
                self.send_message("NickServ", "CONFIRM {}", self.confirm)
                confirmed = True

        self.send("MODE {} +B".format(self.botnick))

        print("DEBUG: Joining")
        
        for channel in self.channels:
            self.join(channel)

        print("DEBUG: Joined")

        while self.running:
            message = self.ircsock.recv(self.recv_size).decode()
            message = message.strip(self.splitter)
            print(message)

            if "raw" in callback:
                callback["raw"](message)

            if "PING :" in message:
                self.ping(message)
                if "ping" in callback:
                    callback["ping"]()
            elif "MODE " in message:
                channel, mode = self.handle_mode(message)
                if "mode" in callback:
                    callback["mode"](channel, mode)
            elif "NICK " in message:
                old_name, new_name = self.handle_rename(message)
                if "nick" in callback:
                    callback["nick"](old_name, new_name)
            elif "KICK " in message:
                kicker = self.handle_kick(message)
                if "kick" in callback:
                    callback["kick"](kicker)
            elif "INVITE " in message:
                channel, name = self.handle_invite(message)
                if "invite" in callback:
                    callback["invite"](channel, name)
            elif "PRIVMSG " in message:
                name, source, response = self.parse(message)
                if source == self.botnick and "pm" in callback:
                    callback["pm"](name, response)
                elif "message" in callback:
                    callback["message"](name, source, response)
            else:
                if "unhandled" in callback:
                    callback["unhandled"](message)
