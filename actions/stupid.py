import re
import operator

def hmm(self, name, source, response):
    check = response.lower().strip()

    botnick = self.bot.botnick
    pattern = re.compile("hm+")
    matches = re.findall(pattern, check)
    maximum = 10
    score = len(matches) if len(matches) <= maximum else maximum

    if len(matches) > 1 and len("".join(re.split(pattern, check))) == 0:
        return

    if name not in self.bot.memories["users"]:
        self.bot.memories["users"][name] = dict()

    if "hmmscore" not in self.bot.memories["users"][name]:
        self.bot.memories["users"][name]["hmmscore"] = 0

    current_score = self.bot.memories["users"][name]["hmmscore"]
    self.bot.memories["users"][name]["hmmscore"] = current_score + score

    self.bot.save_memories()

def hmmscore(self, name, source, response):
    botnick = self.bot.botnick
    score = 0
    score_format = "Hmm score for '{}': {}"

    if " " in response:
        name = response.split(" ", 1)[1].strip()

    if name not in self.bot.memories["users"]:
        self.bot.send_message(source, score_format.format(name, score))
        return

    if "hmmscore" in self.bot.memories["users"][name]:
        score = self.bot.memories["users"][name]["hmmscore"]
        self.bot.send_message(source, score_format.format(name, score))
        return

def hmmscoreboard(self, name, source, response):
    botnick = self.bot.botnick
    hmmscores = list()

    for user, values in self.bot.memories["users"].items():
        hmmscores.append({
            "name": user,
            "score": values.get("hmmscore", 0)
        })

    size = 3
    start = -size

    sort_scores = sorted(hmmscores, key=lambda k: k["score"])
    top_scores = sort_scores[start:][::-1]

    leaders = " | ".join([
        "{} {}".format(ts["name"], ts["score"]) for ts in top_scores
    ])

    self.bot.send_message(source, "Hmm Score Leaderboard: {}".format(leaders))