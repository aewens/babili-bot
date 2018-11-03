import re
import json
import socket
import os.path
import logging
from threading import Thread
from logging.handlers import TimedRotatingFileHandler

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(levelname)s] [%(asctime)s] >> \n%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class Bot:
    def __init__(self, server, port):
        self.ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.logger = logging.getLogger("")
        self.server = server
        self.port = port
        self.channels = []
        self.running = True
        self.crashed = False
        
        self.settings = dict()
        self.places = list()
        self.tasks = None
        self.author = ""
        self.botnick = ""

        self.recv_size = 2048
        self.splitter = "\r\n"

    def send(self, message, *args):
        response = message.format(*args) + "\n"
        password = self.settings.get("password", None)

        if password is not None:
            self.logger.info(response.replace(password, "*" * len(password)))
        else:
            self.logger.info(response)

        print("DEBUG: ", response)
        self.ircsock.send(response.encode())

    def send_message(self, target, message, *args):
        msg = message.format(*args)
        response = "PRIVMSG {0} :{1}".format(target, msg) + "\n"
        password = self.settings.get("password", None)

        if password is not None:
            self.logger.info(response.replace(password, "*" * len(password)))
        else:
            self.logger.info(response)

        print("DEBUG: ", response)
        self.ircsock.send(response.encode())

    def send_action(self, target, message, *args):
        self.send_message(target, "\001ACTION {}\001".format(message), *args)

    def join(self, chan):
        self.send("JOIN {}", chan)
        self.places.append(chan)

        message = ""
        magic_string = "End of /NAMES list."
        while magic_string not in message:
            message = self.ircsock.recv(self.recv_size).decode()
            # message = message.strip(self.splitter)
            print(message)
            self.logger.debug(message)

        list_pattern = re.compile("[@=] {} :".format(chan))
        user_listing = re.split(list_pattern, message)
        if len(user_listing) < 2:
            print("DEBUG: Skipping adding users from {}".format(chan))
            return

        splitter = " {}".format(self.splitter)
        raw_users = user_listing[1].split(splitter)[0].split(" ")
        users = list(filter(self.parse_name, raw_users))
        remember = self.memories["users"]
        for user in users:
            user = self.parse_name(user)

            if user not in remember:
                self.memories["users"][user] = dict()

    def leave(self, chan):
        message = "PART {} :Bye-bye!"
        self.send(message, chan)
        self.places.remove(chan)

    def ping(self, message):
        response = message.split("PING :")[1]
        self.send("PONG :{0}", response)

    def get_name(self, text):
        return text.split("!", 1)[0][1:]

    def parse_name(self, name):
        if name[0] == "~" or name[0] == "@" or name[0] == "+":
            return name[1:]
        else:
            return name

    def parse(self, message):
        before, after = message.split("PRIVMSG ", 1)
        name = self.parse_name(self.get_name(before))
        source, response = after.split(" :", 1)
        return name, source, response

    def handle_mode(self, message):
        before, after = message.split("MODE ", 1)
        name = self.parse_name(self.get_name(before))
        channel, mode = after.split(" ")[:2]
        return channel, mode

    def handle_rename(self, message):
        before, new_name = message.split("NICK ", 1)
        name = self.get_name(before)

        new_name = self.parse_name(new_name)
        name = self.parse_name(name)

        user = self.memories["users"][name]
        del self.memories["users"][name]
        self.memories["users"][new_name] = user
        return user, new_name

    def handle_invite(self, message):
        before, after = message.split("INVITE ", 1)
        name = self.parse_name(self.get_name(before))
        channel = after.split(":", 1)[1]
        self.join(channel)
        return channel, name

    def handle_kick(self, message):
        before, after = message.split("KICK ", 1)
        name = self.parse_name(self.get_name(before))
        return name

    def handle_join(self, message):
        before, after = message.split("JOIN ", 1)
        user = self.parse_name(self.get_name(before))

        if user not in self.memories["users"]:
            self.memories["users"][user] = dict()

        return user

    def handle_part(self, message):
        before, after = message.split("PART ", 1)
        user = self.parse_name(self.get_name(before))
        return user

    def load_memories(self, location):
        path = "{}/{}".format(self.location, location)
        self.memories_path = path

        if not os.path.isfile(path):
            self.memories = {
                "users": dict()
            }
        else:
            with open(path, "r") as f:
                self.memories = json.loads(f.read())

    def thread(self, fn, *args):
        print((self, *args))
        t = Thread(target=fn, args=args)
        t.start()

    def save_memories(self):
        with open(self.memories_path, "w") as f:
            try:
                f.write(json.dumps(self.memories))
            except ValueError as e:
                f.write("")

    def load_settings(self, location):
        set_vars = [
            "author",
            "botnick",
            "channels"
        ]

        path = "{}/{}".format(self.location, location)
        with open(path, "r") as f:
            self.settings = json.loads(f.read())

        for name, attr in self.settings.items():
            if name in set_vars:
                setattr(self, name, attr)

    def stop(self):
        self.send("QUIT :Overheating, powering down")
        self.running = False

    def start(self, config, location, callback):
        message = ""
        registered = False
        confirmed = True

        self.location = location
        self.load_settings(config)
        self.load_memories("data/memories.json")

        logfile = "{}/logs/{}.log".format(self.location, self.botnick)
        logfmt = "[%(levelname)s] [%(asctime)s] >> \n%(message)s"
        datefmt = "%Y-%m-%d %H:%M:%S"
        logger = TimedRotatingFileHandler(logfile, "midnight", 1)
        logger.setLevel(logging.DEBUG)
        logger.setFormatter(logging.Formatter(logfmt, datefmt))
        self.logger.addHandler(logger)

        self.ircsock.connect((self.server, self.port))
        self.send("USER {0} {0} {0} {0}", self.botnick)
        self.send("NICK {0}", self.botnick)

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
            self.logger.debug(message)
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

        if self.tasks is not None:
            if getattr(self.tasks, "run", None) is not None:
                self.tasks.run()

        while self.running:
            message = ""
            while self.splitter not in message:
                message = self.ircsock.recv(self.recv_size).decode()

            message = message.strip(self.splitter)
            self.logger.debug("{}".format(message))

            if ":Closing link:" in message:
                self.logger.warning(message)
                self.stop()
                if "crashed" in callback:
                    callback["crashed"]()
                    break

            if "raw" in callback:
                callback["raw"](message)

            if "PING :" in message:
                self.ping(message)
                if "ping" in callback:
                    callback["ping"]()
            elif "PRIVMSG " in message:
                name, source, response = self.parse(message)
                if source == self.botnick and "pm" in callback:
                    callback["pm"](name, response)
                elif "message" in callback:
                    callback["message"](name, source, response)
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
            elif "JOIN " in message:
                user = self.handle_join(message)
                if "join" in callback:
                    callback["join"](user)
            elif "PART " in message:
                user = self.handle_part(message)
                if "part" in callback:
                    callback["part"](user)
            elif "INVITE " in message:
                channel, name = self.handle_invite(message)
                if "invite" in callback:
                    callback["invite"](channel, name)
            elif "unhandled" in callback:
                callback["unhandled"](message)