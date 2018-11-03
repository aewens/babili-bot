from xml.etree import ElementTree as etree
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from json import loads, dumps
from re import sub

class RSS:
    def __init__(self, state):
        self.name = "RSS"
        self.bot = state["bot"]
        self.alias = state["alias"]
        self.use = state["use"]
        self.source = state["source"]
        self.channels = state["channels"]
        self.memory = state.get("memory", {
            "initialized": False,
            "known": list()
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
            "use": self.use,
            "source": self.source,
            "channels": self.channels,
            "memory": self.memory
        }

    def cache(self, item):
        guid = item.findtext("guid", None)
        if guid is not None:
            self.memory["known"].append(guid)

    def mirror(self, item):
        guid = item.findtext("guid", None)
        if guid is None:
            return
        
        if guid in self.memory["known"]:
            return

        self.memory["known"].append(guid)
        
        use = sub(r"(<\/?[^>]+>)|\n", "", item.findtext(self.use, ""))
        user = item.findtext("author", "").split("@")[0]
        post = "{} (posted by {}) <{}>".format(use, user, guid)
        response = "[{}] {}".format(self.alias, post)
        for channel in self.channels:
            self.bot.send_message(channel, response)

    def fetch(self, callback):
        req = Request(self.source)
        try:
            response = urlopen(req).read()
        except HTTPError:
            return
        except URLError:
            return

        feed = etree.fromstring(response)
        items = feed.findall("channel/item")
        for item in items:
            callback(item)
