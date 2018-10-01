import re
import operator

def capitalize(word):
    return word[0].upper() + word[1:]

def score_word(word, regex):
    def wording(self, name, source, response):
        check = response.lower().strip()

        botnick = self.bot.botnick
        pattern = re.compile(regex)#"hm+")
        matches = re.findall(pattern, check)
        maximum = 10
        score = len(matches) if len(matches) <= maximum else maximum

        if len(matches) > 1 and len("".join(re.split(pattern, check))) == 0:
            return

        if name not in self.bot.memories["users"]:
            self.bot.memories["users"][name] = dict()

        keyword = "{}score".format(word)

        if keyword not in self.bot.memories["users"][name]:
            self.bot.memories["users"][name][keyword] = 0

        current_score = self.bot.memories["users"][name][keyword]
        self.bot.memories["users"][name][keyword] = current_score + score

        self.bot.thread(self.bot.save_memories)
    return wording

def wordscore(word):
    def scoring(self, name, source, response):
        botnick = self.bot.botnick
        score = 0
        score_format = "%s score for '{}': {}" % (capitalize(word))

        if " " in response:
            name = response.split(" ", 1)[1].strip()

        if name not in self.bot.memories["users"]:
            self.bot.send_message(source, score_format.format(name, score))
            return

        keyword = "{}score".format(word)

        if keyword not in self.bot.memories["users"][name]:
            self.bot.send_message(source, score_format.format(name, score))
            return
            
        score = self.bot.memories["users"][name][keyword]
        self.bot.send_message(source, score_format.format(name, score))
    return scoring

def wordscoreboard(word):
    def scoreboard(self, name, source, response):
        botnick = self.bot.botnick
        scores = list()

        for user, values in self.bot.memories["users"].items():
            scores.append({
                "name": user,
                "score": values.get("{}score".format(word), 0)
            })

        size = 3
        start = -size

        sort_scores = sorted(scores, key=lambda k: k["score"])
        top_scores = sort_scores[start:][::-1]

        leaders = " | ".join([
            "{} {}".format(ts["name"], ts["score"]) for ts in top_scores
        ])

        response = "{} Score Leaderboard: {}".format(capitalize(word), leaders)

        self.bot.send_message(source, response)
    return scoreboard