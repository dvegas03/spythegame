import os
from dotenv import load_dotenv

load_dotenv()

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")
SPY_BOT_TESTING_CHANNEL_ID = "C05KVE9CA9E"
BOT_USER_ID = os.environ.get("BOT_USER_ID")
