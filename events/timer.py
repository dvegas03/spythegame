import time
from slack_sdk import WebClient
from config import settings

# Timer class. Handles the timer event in the game


class Timer:
    def __init__(self, token=settings.SLACK_BOT_TOKEN):
        self.client = WebClient(token=token)
        self.channel_id = settings.SPY_BOT_TESTING_CHANNEL_ID

    def start_timer(self, duration_seconds, callback):
        response = self.client.chat_postMessage(
            channel=self.channel_id, text=f"Time remaining: {duration_seconds} seconds"
        )

        message_ts = response["ts"]
        for i in range(duration_seconds, 0, -1):
            time.sleep(1)

            self.client.chat_update(
                channel=self.channel_id,
                ts=message_ts,
                text=f"Time remaining: {i - 1} seconds",
            )

        self.client.chat_postMessage(channel=self.channel_id, text="Time's up!")

        callback()
