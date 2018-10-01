from actions.botlist import botlist
from actions.access import banish, pardon
from actions.control import puppet, inject, nomad
from actions.web import summon, whois, how_dare_you
from actions.stupid import score_word, wordscore, wordscoreboard

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
    },
    {
        "type": "response",
        "pattern": "/!summon \S+ .+/",
        "callback": summon
    },
    {
        "type": "response",
        "pattern": "/!summon \S+$/",
        "callback": how_dare_you
    },
    {
        "type": "response",
        "pattern": "/!banish \S+ .+/",
        "callback": banish
    },
    {
        "type": "response",
        "pattern": "/!pardon \S+/",
        "callback": pardon
    },
    {
        "type": "response",
        "pattern": "/!puppet \S+ .+/",
        "callback": puppet
    },
    {
        "type": "response",
        "pattern": "/!inject \S+/",
        "callback": inject
    },
    {
        "type": "response",
        "pattern": "/!nomad \S+ \S+/",
        "callback": nomad
    },
    {
        "type": "response",
        "pattern": "/hm+/",
        "callback": score_word("hmm", "hm+")
    },
    {
        "type": "response",
        "pattern": "/!hmmscore(\s|$)/",
        "callback": wordscore("hmm")
    },
    {
        "type": "response",
        "pattern": "!hmmscoreboard",
        "callback": wordscoreboard("hmm")
    },
    {
        "type": "response",
        "pattern": "/o+f/",
        "callback": score_word("oof", "o+f")
    },
    {
        "type": "response",
        "pattern": "/!oofscore(\s|$)/",
        "callback": wordscore("oof")
    },
    {
        "type": "response",
        "pattern": "!oofscoreboard",
        "callback": wordscoreboard("oof")
    },
    {
        "type": "response",
        "pattern": "/!whois \S+/",
        "callback": whois
    }
]