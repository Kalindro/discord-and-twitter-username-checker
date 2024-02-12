import glob
import os
import random
import time

import requests
from dotenv import load_dotenv
from requests.exceptions import HTTPError, Timeout, TooManyRedirects

from src.utils.dir_paths import INPUTS_DIR, OUTPUTS_DIR
from src.utils.logger_custom import default_logger as logger
from src.utils.user_agents import user_agents


class UsernameChecker:
    def __init__(self):
        # ### Static settings # ###
        load_dotenv()
        self.TIMEOUT = 7
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

        for index, username in enumerate(self.input_usernames):
            logger.info(f"Checking discord username number {index}...")
            response = self.discord_username_availability(username)
            if response:
                discord_usernames_list.append(username)
            time.sleep(1)
            if index % 2 == 0:
                time.sleep(random.randint(10, 12))

        for index, username in enumerate(discord_usernames_list):
            logger.info(f"Checking twitter username number {index}...")
            response = self.twitter_username_availability(username)
            if response:
                both_usernames_list.append(username)
            time.sleep(1)

        filename = os.path.join(OUTPUTS_DIR, "valid_usernames.txt")
        with open(filename, 'w') as file:
            for username in both_usernames_list:
                file.write(username + '\n')

        logger.success(f"Finished checking usernames, saved file")
        return both_usernames_list

    def discord_username_availability(self, username: str) -> bool:
        try:
            url = f"{self.discord_url}/{username}"
            response = requests.get(url, timeout=self.TIMEOUT)

            if response.json()["data"]["check"]["status"] == 2:
                return True
            else:
                return False

        except (HTTPError, Timeout, TooManyRedirects) as err:
            logger.error(f"Failed on {username}, sleeping a bit, error: {err}")
            time.sleep(15)

        except Exception as err:
            logger.error(f"Failed on {username}, error: {err}")

    def twitter_username_availability(self, username) -> bool:
        try:
            user_agent = random.choice(user_agents)
            response = requests.get(
                f"https://twitter.com/i/api/i/users/username_available.json?username={username}", headers={
                    "authorization": f"Bearer {self.twitter_bearer_token}",
                    "x-guest-token": "1337",
                    "x-twitter-active-user": "yes",
                    "x-twitter-client-language": "en",
                    "user-agent": user_agent,
                }, timeout=self.TIMEOUT
            )

            if response.json()["valid"]:
                return True
            else:
                return False

        except (HTTPError, Timeout, TooManyRedirects) as err:
            logger.error(f"Failed on {username}, sleeping a bit, error: {err}")
            time.sleep(15)

        except Exception as err:
            logger.error(f"Failed on {username}, error: {err}")

    @staticmethod
    def shuffle_list() -> None:
        filename = os.path.join(OUTPUTS_DIR, "valid_usernames.txt")
        with open(filename, 'r') as file:
            usernames_list = file.read().split()
            random.shuffle(usernames_list)
            usernames_list = list(set(usernames_list))

        with open(filename, 'w') as file:
            for username in usernames_list:
                file.write(username + '\n')


if __name__ == "__main__":
    mode = 2
    checker = UsernameChecker()
    if mode == 1:
        checker.check_usernames_availability_both()
        checker.shuffle_list()
    if mode == 2:
        checker.shuffle_list()
