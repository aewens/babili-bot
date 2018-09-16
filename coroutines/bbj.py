from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError
from datetime import datetime
from json import loads, dumps
from re import sub

class BBJ:
    def __init__(self, state):
        self.name = "BBJ"
        self.bot = state["bot"]
        self.alias = state["alias"]
        self.source = state["source"]
        self.channels = state["channels"] 
        self.memory = state.get("memory", {
            "initialized": False,
            "known": dict()
        })

    def start(self):
        if not self.memory["initialized"]:
            self.memory["initialized"] = True
            self.fetch(self.cache)
        return self.run()

    def run(self):
        self.fetch(self.mirror)
        return {
            "bot": self.bot,
            "alias": self.alias,
            "source": self.source,
            "channels": self.channels,
            "memory": self.memory
        }

    def cache(self, item):
        self.memory["known"][item["thread_id"]] = item["last_mod"]

    def process_thread(self, thread_id, thread):
        data = thread.get("data", dict())
        title = data.get("title", "")
        replies = data.get("reply_count", "")
        messages = data.get("messages", "")
        usermap = thread.get("usermap", dict())
        reply = messages[replies]
        author = reply.get("author", "")
        username = usermap[author].get("user_name", "")
        body = reply.get("body", "")
        body = sub(r">>\d\n\n", r"", body)
        body = sub(r"\n", r" ", body)
        php = "https://bbj.tilde.team/index.php"
        link = "{}?thread_id={}".format(php, thread_id)
        for channel in self.channels:
            response = "'{}' ({}) : {} <{}>".format(title, username, body, link)
            message = "[{}] {}".format(self.alias, response)
            self.bot.send_message(channel, message)

    def get_thread(self, thread_id, callback):
        params = {
            "thread_id": thread_id
        }
        post_params = str(dumps(params)).encode()
        thread_load = Request("{}/thread_load".format(self.source), post_params)
        thread_load.add_header("Content-Type", "application/json")

        try:
            response = callback(thread_id, loads(urlopen(thread_load).read()))
        except HTTPError:
            return

    def mirror(self, item):
        thread_id = item["thread_id"]
        last_mod = self.memory["known"][thread_id]
        if last_mod == item["last_mod"]:
            return

        self.memory["known"][thread_id] = item["last_mod"]
        self.get_thread(thread_id, self.process_thread)

    def fetch(self, callback):
        thread_index = Request("{}/thread_index".format(self.source))

        try:
            response = loads(urlopen(thread_index).read())
            threads = response.get("data", dict())
            for thread in threads:
                callback(thread)
        except HTTPError:
            return