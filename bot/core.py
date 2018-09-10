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

        self.recv_size = 2048

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
            message = message.strip("\n\r")
            print(message)

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

    def parse(self, message):
        before, after = message.split("PRIVMSG ", 1)
        name = before.split("!", 1)[0][1:]
        source, response = after.split(" :", 1)
        return name, source, response

    def track_rename(self, message):
        before, new_name = message.split("NICK ", 1)
        name = before.split("!", 1)[0][1:]
        user = self.users[name]
        del self.users[name]
        self.users[new_name] = user

    def answer_invite(self, message):
        before, after = message.split("INVITE ", 1)
        channel = after.split(":", 1)[1]
        self.join(channel)

    def log_kick(self, message):
        # :aewens!aewens@rightful.heir.to.chaos KICK #insane BabiliBot|py :aewens
        regex = "KICK #\S+ {} :".format(self.botnick)
        before, kicker = re.split(regex, message)
        self.kickers.append(kicker)

    def load_settings(self, location):
        with open(location, "r") as f:
            self.settings = json.loads(f.read())

    def stop(self):
        self.running = False
        self.send("QUIT")

    def start(self, callback, settings):
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

        magic_string = "MODE {} +r".format(self.botnick)
        while magic_string not in message:
            message = self.ircsock.recv(self.recv_size).decode()
            message = message.strip("\n\r")
            print(message)
            if not registered and "Password accepted" in message:
                registered = True
            if not registered and "choose a different nick" in message:
                self.send_message("NickServ", "IDENTIFY {}", password)
            if not confirmed and "Your account will expire" in message:
                self.send_message("NickServ", "CONFIRM {}", self.confirm)
                confirmed = True

        self.send("MODE {} +B".format(self.botnick))

        print("DEBUG: Joining")
        
        for channel in self.channels:
            self.join(channel)

        print("DEBUG: Joined")

        while self.running:
            message = self.ircsock.recv(self.recv_size).decode()
            message = message.strip("\n\r")
            print(message)

            if "PING :" in message:
                self.ping(message)
            elif "NICK " in message:
                self.track_rename(message)
            elif "INVITE " in message:
                self.answer_invite(message)
            elif "PRIVMSG" in message:
                name, source, response = self.parse(message)
                callback(name, source, response)