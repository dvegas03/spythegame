from assets.buttons import start_game_button, ready_to_play_button
from config import settings
from slack_bolt.context.say import Say
from slack_sdk import WebClient
from assets import categories
from events import timer
from events import vote
import random


class SpyGame:
    def __init__(self, app, client):
        self.app = app
        self.client = client
        self.active_voting_handler = None
        self.players = {}
        self.round_number = 1
        self.max_rounds = 10
        self.round_time = 120

    # Adds players to the active players list
    def _add_player(self, user_id, say):
        user_info = self.client.users_info(user=user_id)
        user_name = user_info["user"]["name"]

        if user_id not in self.players:
            self.players[user_id] = {"name": user_name, "role": None, "alive": True}
            say(f"{user_name} has joined the game!")
            return True
        else:
            say(f"{user_name}, you're already in the game!")
            return False

    # /start command method
    def start_game(self, ack, say, body):
        ack()
        user_id = body.get("user_id", body.get("user", {}).get("id", None))

        self._add_player(user_id, say)
        say(blocks=[start_game_button()])

        self.client.chat_postEphemeral(
            channel=body.get("channel_id"),
            user=user_id,
            text="Ready to start the game?",
            blocks=[ready_to_play_button()],
        )

    # Handles ready-to-play button. Starts the game, assigns the players' roles
    def handle_ready_play(self, ack, body, say: Say, context, **kwargs):
        ack()
        player_names = [player_data["name"] for player_data in self.players.values()]
        newline = '\n'
        say(f"The game has started! Players in the game: {newline.join(player_names)}")


        spy = random.choice(list(self.players.keys()))
        country = random.choice(categories.Countries)

        for player_id, player_data in self.players.items():
            if player_id == spy:
                player_data["role"] = "spy"
                role_message = "You're a spy, do your best to remain unnoticed."
            else:
                player_data["role"] = "local"
                role_message = (
                    f"You're local in {country}, do your best to recognize the spy."
                )

            context.client.chat_postEphemeral(
                channel=body["channel"]["id"], user=player_id, text=role_message
            )

        for player_id in self.players:
            self.players[player_id]["alive"] = True
            self.players[player_id]["location"] = (
                country if self.players[player_id]["role"] == "local" else None
            )

        self.start_round(say)

    # Starts round according to the game's logic
    def start_round(self, say):
        say(f"Round {self.round_number} has been started!")
        self.active_voting_handler = vote.VotingHandler(
            self.players, self.vote_finished_callback, self.app, say, self.client
        )
        print("Voting Handler is Active")
        timer_instance = timer.Timer()
        timer_instance.start_timer(
            self.round_time, self.active_voting_handler.start_vote
        )

    # Callback function for vote.py
    def vote_finished_callback(self, voted_out_player_name, say):
        for player_id, player in self.players.items():
            if player["name"] == voted_out_player_name:
                player["alive"] = False
                break

        if self.check_end_game():
            self.end_game(say)
        else:
            self.round_number += 1
            self.start_round(say)

    # Checks if the game has been ended
    def check_end_game(self):
        alive_players = [player for player in self.players.values() if player["alive"]]
        if len(alive_players) == 1 and alive_players[0]["role"] == "spy":
            return True
        if any(
            player["role"] == "spy" and not player["alive"]
            for player in self.players.values()
        ):
            return True
        if self.round_number >= self.max_rounds:
            return True

        return False

    # CLears variables, end game
    def end_game(self, say):
        say("The game has ended!")
        self.players = {}
        self.round_number = 1
        self.active_voting_handler = None

    def get_active_voting_handler(self):
        return self.active_voting_handler


app = settings.App
client = WebClient(token=settings.SLACK_BOT_TOKEN)
