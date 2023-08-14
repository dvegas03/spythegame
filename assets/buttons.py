def start_game_button():
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "Interested in joining the game? Let us know by clicking below:",
        },
        "accessory": {
            "type": "button",
            "style": "primary",
            "text": {
                "type": "plain_text",
                "text": ":white_check_mark: Join Game",
                "emoji": True,
            },
            "action_id": "start_game_button",
        },
    }


def ready_to_play_button():
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "Ready to jump into the action? Click the button below:",
        },
        "accessory": {
            "type": "button",
            "style": "primary",
            "text": {
                "type": "plain_text",
                "text": ":rocket: Ready to Play",
                "emoji": True,
            },
            "action_id": "ready_to_play_button",
        },
    }
