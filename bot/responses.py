import re

class Responses:
    def __init__(self, bot):
        self.bot = bot
        self.triggers = {
            "name": dict(),
            "source": dict(),
            "response": dict()
        }

    def add_trigger(self, trigger_type, pattern, callback):
        if trigger_type in self.triggers:
            self.triggers[trigger_type][pattern] = callback

    def parse(self, name, source, response):
        check = {
            "name": name,
            "source": source,
            "response": response
        }

        for trigger in list(self.triggers.keys()):
            for pattern, callback in self.triggers[trigger].items():
                if pattern[0] == "!" and pattern == response:
                    callback(self, name, source, response)
                else:
                    regex = re.compile(pattern)
                    if regex.match(check[trigger]) is not None:
                        callback(self, name, source, response)