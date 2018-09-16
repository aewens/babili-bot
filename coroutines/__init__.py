from coroutines.bbj import BBJ

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
            "source": "http://localhost:7099/api",
            "channels": ["#insane"], #team
        }
    }
]