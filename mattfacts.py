import os
import time
import json
import urllib2
import datetime
import webbrowser
from slackclient import SlackClient
from random import randint

# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")
RIOT_API = os.environ.get("RIOT_API")

# constants
AT_BOT = "<@" + BOT_ID + ">"
FACT = "fact"
ALTFACT = "alternative fact"
RANK = "rank"
PICTURE = "pic"
MATT_BIRTHDAY = datetime.date(1990, 11, 7)
TODAY = datetime.date.today()
DIFF = TODAY - MATT_BIRTHDAY

RESPONSES = ("Matt was physically born a boy and mentally a sandwich.", "Matt has diabetes.", "Matt and Mott are synonyms.",
    "Matt is " + str(DIFF.days) + " days old!", "Matt is a weird guy, but he is fun.")
ALT_RESPONSES = ("Matt only has 9 toes on his feet, his tenth toe is his penis.", "Matt has the ability to suck his own ear.",
    "Matt invented the sport of penis wrestling, he plays alone.", "Matt was once on the path of going pro in LoL, but diabetes derailed his destiny.",
    "Before becoming diabetic, Matt has straight hair.")
picture_url = 'https://graph.facebook.com/853470163/picture?width=9999&height=9999'
json_games = urllib2.urlopen('https://na.api.pvp.net/api/lol/na/v2.5/league/by-summoner/31203597/entry?api_key=' + RIOT_API)
games = json.load(json_games)

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_TOKEN'))


def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    """
        Finds a random number between 0 and response length - 1,
        and returns corresponding fact from RESPONSES
    """
    if command.startswith(FACT):
        random_fact_number = randint(0, len(RESPONSES) - 1)
        response = RESPONSES[random_fact_number]
    elif command.startswith(ALTFACT):
        random_fact_number = randint(0, len(ALT_RESPONSES) - 1)
        response = ALT_RESPONSES[random_fact_number]
    elif command.startswith(RANK):
        tier = games['31203597'][0]['tier']
        division = games['31203597'][0]['entries'][0]['division']
        flex_tier = games['31203597'][1]['tier']
        flex_division = games['31203597'][1]['entries'][0]['division']
        response = "Solo Rank: " + tier + " " + division + "\n" + "Flex Rank: " + flex_tier + " " + flex_division
    elif command.startswith(PICTURE):
        response = picture_url
    else:
        response = "I DON'T KNOW HOW TO DO THAT."
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
