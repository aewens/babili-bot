from urllib.request import Request, urlopen
from urllib.error import HTTPError
from json import loads

def whois(self, name, source, response):
    botnick = self.bot.botnick
    domain = response.split("!whois ")[1]

    api_url = "https://api.jsonwhoisapi.com/v1/whois"
    api_key = self.bot.settings.get("extras", dict()).get("jsonwhoisapi", "")

    req = Request("{}?identifier={}".format(api_url, domain))
    req.add_header("Authorization", api_key)

    try:
        data = loads(urlopen(req).read())
    except HTTPError:
        self.bot.send_message(source, "{} cannot exist".format(domain))
        return

    registered = data.get("registered", None)
    if registered is not None:
        nameservers = len(data.get("nameservers", ""))
        registrar = data.get("registrar", dict())
        is_registered = "id" in registrar or nameservers > 0
        status = "registered" if is_registered else "available"
        self.bot.send_message(source, "{} is '{}'".format(domain, status))
    else:
        self.bot.send_message(source, "{} might be available".format(domain))