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

    def join(self, chan, confirmed=False):
        self.send("JOIN {}", chan)

        message = ""
        magic_string = "End of /NAMES list."
        while magic_string not in message:
            message = self.ircsock.recv(self.recv_size).decode()
            message = message.strip("\n\r")
            print(message)

    def ping(self, message):
        response = message.split("PING :")[1]
        self.send("PONG :{0}", response)

    def parse(self, message):
        before, after = message.split("PRIVMSG ", 1)
        name = before.split("!", 1)[0][1:]
        source, response = after.split(" :", 1)
        return name, source, response

    def load_settings(self, location):
        with open(location, "r") as f:
            self.settings = json.loads(f.read())

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

        print("DEBUG: Joining")
        
        for channel in self.channels:
            self.join(channel)

        print("DEBUG: Joined")

        while self.running:
            message = self.ircsock.recv(self.recv_size).decode("UTF-8")
            message = message.strip('\n\r')
            print(message)

            if "PRIVMSG" in message:
                name, source, response = self.parse(message)
                callback(name, source, response)
            if "PING :" in message:
                self.ping(message)

            

    # = #channel :