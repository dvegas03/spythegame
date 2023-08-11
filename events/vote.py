from slack_sdk import WebClient
from config.settings import SLACK_BOT_TOKEN, SPY_BOT_TESTING_CHANNEL_ID
import logging

logging.basicConfig(level=logging.INFO)
CHANNEL = SPY_BOT_TESTING_CHANNEL_ID

# VotingHandler class handles the voting event in the game


class VotingHandler:
    def __init__(self, players, callback, app, say, client):

        self.players = players
        self.votes = {player_id: 0 for player_id in players}
        self.players_voted = set()
        self.callback = callback
        self.app = app
        self.say = say
        self.client = client

    def start_vote(self):
        self.post_voting_message()

    # Posting the voting message
    def post_voting_message(self):
        blocks = self.create_message_blocks()
        self.client.chat_postMessage(
            channel=CHANNEL,
            text="Voting time! Vote for the player you think is the spy.",
            blocks=blocks,
        )
        logging.info("Posted voting message.")

    # Creating message blocks for each player
    def create_message_blocks(self):
        return [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "Voting time! Vote for the player you think is the spy:"},
            },
            {
                "type": "actions",
                "elements": [self.create_button(player_id) for player_id in self.players if self.players[player_id]['alive']],
            },
        ]
    # Creating a button for each player
    def create_button(self, player_id):
        return {
            "type": "button",
            "text": {"type": "plain_text", "text": f"{self.players[player_id]['name']} ({self.votes[player_id]})"},
            "action_id": f"vote_{player_id}",
        }
    # Handles the vote button press event
    def handle_vote(self, vote):
        logging.info("Handling vote.")
        voted_for = vote["action_id"].split("_")[1]
        user_id = vote['user']['id']

        if user_id not in self.players or user_id in self.players_voted:
            self.client.chat_postEphemeral(
                channel=vote["channel"]["id"],
                user=user_id,
                text="You can't vote or have already voted.",
            )
            return

        self.votes[voted_for] += 1
        self.players_voted.add(user_id)
        self.update_voting_message(vote["channel"]["id"], vote['message']['ts'])

        if len(self.players_voted) == sum(player['alive'] for player in self.players.values()):
            self.finish_voting()
            logging.info("All alive players have voted.")
    # Updates the number of votes next to the players name
    def update_voting_message(self, channel_id, message_ts):
        logging.info("Updating voting message.")
        blocks = self.create_message_blocks()
        self.client.chat_update(
            channel=channel_id,
            ts=message_ts,
            text="Updated voting results",
            blocks=blocks,
        )

    #Finishes voting process
    def finish_voting(self):
        logging.info("Finishing voting.")
        winner_id = self.get_max_voted_player()
        self.reveal_player_role(winner_id)
        self.callback(self.players[winner_id]['name'], self.say)
        self.reset()

    # Resets the VotingHandler
    def reset(self):
        self.votes = {player_id: 0 for player_id in self.players}
        self.players_voted = set()
    
    # Reveals the players' role
    def reveal_player_role(self, player_id):
        role = self.players[player_id]['role']
        self.client.chat_postMessage(
            channel=CHANNEL,
            text=f"{self.players[player_id]['name']} was the {role}!",
        )

    def get_max_voted_player(self):
        return max(self.votes, key=self.votes.get)
