from subprocess import Popen, PIPE
from email.mime.text import MIMEText
    
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError
from json import loads

def get_iden(devices, device_name):
    for device in devices:
        if device.get("nickname", "") == device_name:
            return device.get("iden", "")

def push_note(bot, title, body):
    api_url = "https://api.pushbullet.com/v2"
    extra_settings = bot.settings.get("extras", dict())
    pb_settings = extra_settings.get("pushbullet", dict())
    api_key = pb_settings.get("api", "")
    device_name = pb_settings.get("device", "")

    list_devices = Request("{}/devices".format(api_url))
    list_devices.add_header("Access-Token", api_key)

    try:
        data = loads(urlopen(list_devices).read())
    except HTTPError:
        return

    devices = data.get("devices", list())
    iden = get_iden(devices, device_name)

    params = {
        "device_iden": iden,
        "type": "note",
        "title": title,
        "body": body
    }

    post_params = urlencode(params).encode()

    pushes = Request("{}/pushes".format(api_url), post_params)
    pushes.add_header("Access-Token", api_key)

    try:
        response = loads(urlopen(pushes).read())
    except HTTPError as e:
        return

def summon(self, name, source, response):
    botnick = self.bot.botnick
    author = self.bot.author
    user, reason = response.split("!summon ")[1].split(" ", 1)

    email = "{}@tilde.team"
    subject = "You have been summoned!"

    text = " ".join([
        "My bot, {}, received a summoning request for you".format(botnick),
        "from {} in channel {} for reason: {}".format(name, source, reason)
    ])
    message = MIMEText(text)

    message["From"] = email.format(botnick)
    message["To"] = email.format(user)
    message["Subject"] = subject

    command = "/usr/sbin/sendmail -t -oi".split(" ")
    p = Popen(command, stdin=PIPE, universal_newlines=True)
    p.communicate(message.as_string())

    if user == author:
        push_note(self.bot, subject, text)
    
    confirmation = "{}: You have summoned {}".format(name, user)
    self.bot.send_message(source, confirmation)

def how_dare_you(self, name, source, response):
    user = response.split("!summon ")[1]
    rude = "{}: You think you can just summon someone without a reason? Rude."
    self.bot.send_message(source, rude.format(user))

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
        
    registered = data.get("registered", False)
    nameservers = len(data.get("nameservers", list())) > 0
    self.bot.logger.debug("WHOIS: {}".format(data))

    if registered and nameservers:
        self.bot.send_message(source, "{} is '{}'".format(domain, "registered"))
    elif not (registered or nameservers):
        self.bot.send_message(source, "{} is '{}'".format(domain, "available"))
    else:
        self.bot.send_message(source, "{} might be available".format(domain))