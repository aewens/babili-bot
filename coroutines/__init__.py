from coroutines.bbj import BBJ
from coroutines.rss import RSS

# {
#     "worker": test,
#     "interval": 3
# }
# def test(bot):
#     print("Testing {}".format(bot.botnick))

coroutines = [
    {
        "worker": lambda state: BBJ(state).start(),
        "interval": 5,
        "state": {
            "alias": "bbj",
            "source": "http://localhost:7099/api",
            "channels": ["#team"]
        }
    },
    {
        "worker": lambda state: RSS(state).start(),
        "interval": 6,
        "state": {
            "alias": "title",
            "source": "https://tilde.news/newest.rss",
            "use": "title",
            "channels": ["#meta", "#tildeverse"]
        }
    },
    {
        "worker": lambda state: RSS(state).start(),
        "interval": 8,
        "state": {
            "alias": "links-comments",
            "source": "https://tilde.news/comments.rss",
            "use": "description",
            "channels": ["#tildeverse"]
        }
    }
]