import glob
import os
import random
import time

import requests
from dotenv import load_dotenv

from src.utils.dir_paths import INPUTS_DIR, OUTPUTS_DIR
from src.utils.logger_custom import default_logger as logger
from src.utils.user_agents import user_agents


class UsernameChecker:
    def __init__(self):
        load_dotenv()
        self.TIMEOUT = 5
        self.amount_usernames_output = 50
        self.discord_url = "https://api.lixqa.de/v3/discord/pomelo"
        self.input_usernames = self._input_usernames
        self.twitter_bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

    @property
    def _input_usernames(self) -> list:
        filepath = glob.glob(INPUTS_DIR + '*.txt')
        if len(filepath) > 1:
            raise ValueError("Multiple files in input folder")
        with open(filepath[0], 'r') as file:
            return file.read().split()

    def check_usernames_availability_both(self) -> list:
        logger.info("Starting checking usernames")
        both_usernames_list = []
        discord_usernames_list = []

        while len(both_usernames_list) < self.amount_usernames_output:
            for index, username in enumerate(self.input_usernames):
                logger.info(f"Checking discord username number {index}...")
                response = self.discord_username_availability(username)
                if response["data"]["check"]["status"] == 2:
                    discord_usernames_list.append(username)
                if index % 2 == 0:
                    time.sleep(11)

            for index, username in enumerate(discord_usernames_list):
                logger.info(f"Checking twitter username number {index}...")
                response = self.twitter_username_availability(username)
                if response["valid"]:
                    both_usernames_list.append(username)
                time.sleep(1)

            filename = os.path.join(OUTPUTS_DIR, "valid_usernames.txt")
            with open(filename, 'w') as file:
                for username in both_usernames_list:
                    file.write(username + '\n')

        logger.success(f"Finished checking {self.amount_usernames_output}, saved file")
        return both_usernames_list

    def discord_username_availability(self, username: str) -> dict:
        try:
            url = f"{self.discord_url}/{username}"
            response = requests.get(url)
            response.raise_for_status()

            return response.json()

        except Exception as err:
            logger.exception(f"Error: {err}")

    def twitter_username_availability(self, username):
        try:
            user_agent = random.choice(user_agents)
            response = requests.get(
                f"https://twitter.com/i/api/i/users/username_available.json?username={username}", headers={
                    "authorization": f"Bearer {self.twitter_bearer_token}",
                    "x-guest-token": "1337",
                    "x-twitter-active-user": "yes",
                    "x-twitter-client-language": "en",
                    "user-agent": user_agent,
                }, )

            return response.json()

        except Exception as err:
            logger.exception(f"Error: {err}")


if __name__ == "__main__":
    checker = UsernameChecker()
    checker.check_usernames_availability_both()
