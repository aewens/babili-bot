from actions.botlist import botlist

actions = [
    {
        "type": "response",
        "pattern": "!botlist",
        "callback": botlist
    },
    {
        "type": "response",
        "pattern": "!rollcall",
        "callback": botlist
    }
]