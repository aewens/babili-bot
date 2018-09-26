from actions.botlist import botlist
from actions.web import summon, whois
from actions.access import banish, pardon
from actions.control import puppet, inject, nomad
from actions.stupid import hmm, hmmscore, hmmscoreboard

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
        "callback": hmm
    },
    {
        "type": "response",
        "pattern": "/!hmmscore(\s|$)/",
        "callback": hmmscore
    },
    {
        "type": "response",
        "pattern": "!hmmscoreboard",
        "callback": hmmscoreboard
    },
    {
        "type": "response",
        "pattern": "/!whois \S+/",
        "callback": whois
    }
]