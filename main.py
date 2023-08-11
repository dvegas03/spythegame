import logging
import re

# Slack-API imports
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient

# Local imports
from config import settings
from events.handle_game import SpyGame

# Logging setup
logging.basicConfig(level=logging.INFO)

class SpyBot:

    def __init__(self):
        self.app = settings.App(token=settings.SLACK_BOT_TOKEN)
        self.client = WebClient(token=settings.SLACK_BOT_TOKEN)
        settings.app = self.app
        self.game_instance = SpyGame(self.app, self.client)
        self.setup_event_listeners()

    # Event listeneres
    def setup_event_listeners(self):
        @self.app.command("/start")
        def handle_start_command(ack, say, command, client):
            ack()
            self.game_instance.start_game(ack, say, command)

        @self.app.action("start_game_button")
        def handle_start_game_action(ack, body, say):
            ack()
            self.game_instance._add_player(body['user']['id'], say)

        @self.app.action("ready_to_play_button")
        def handle_ready_play_action(ack, body, say, context, **kwargs):
            ack()
            self.game_instance.handle_ready_play(ack, body, say, context, **kwargs)

        @self.app.action(re.compile("vote_.*"))
        def vote_action_listener(ack, body, client, context):
            ack()
            voting_handler = self.game_instance.get_active_voting_handler()
            if voting_handler:
                vote = body['actions'][0]
                vote.update({
                    'user': body['user'],
                    'channel': body['channel'],
                    'message': body['message']
                })
                voting_handler.handle_vote(vote)

if __name__ == "__main__":
    bot = SpyBot()
    SocketModeHandler(bot.app, settings.SLACK_APP_TOKEN).start()
