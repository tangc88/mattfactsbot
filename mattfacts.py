import os
import time
import json
import urllib2
from slackclient import SlackClient
from random import randint

# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
FACT = "fact"
ALTFACT = "alternative fact"
RANK = "rank"
RESPONSES = ("Matt was physically born a boy and mentally a sandwich.", "Matt has diabetes.", "Matt and Mott are synonyms.",
            "Matt only has 9 toes.", "Matt has the ability to suck his own ear")
ALT_RESPONSES = ("Matt only has 9 toes.", "Matt has the ability to suck his own ear.")
json_games = urllib2.urlopen('https://na.api.pvp.net/api/lol/na/v2.5/league/by-summoner/31203597/entry?api_key=ea292ea8-35ca-4f74-9d2c-ab12d67d6fe0')
games = json.load(json_games)

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))


def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
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
    else:
        response = "Sure...write some more code then I can do that!"
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
