import os
import time

import requests

from src.utils.dir_paths import INPUTS_DIR, OUTPUTS_DIR
from src.utils.logger_custom import default_logger as logger


class UsernameChecker:
    def __init__(self):
        self.TIMEOUT = 5
        self.discord_url = "https://api.lixqa.de/v3/discord/pomelo"
        self.input_usernames = self._input_usernames

    @property
    def _input_usernames(self) -> list:
        filepath = os.path.join(INPUTS_DIR, "input_usernames.txt")
        with open(filepath, 'r') as file:
            return file.read().split()

    def _send_discord_request(self, username: str) -> dict:
        try:
            url = f"{self.discord_url}/{username}"
            response = requests.get(url)
            response.raise_for_status()
            return response.json()

        except Exception as err:
            logger.exception(f"Error: {err}")

    def check_usernames(self) -> list:
        logger.info("Starting checking usernames")
        valid_usernames_list = []
        request_counter = 0

        for username in self.input_usernames:
            logger.info(f"Checking username number {request_counter}...")
            response = self._send_discord_request(username)
            if response["data"]["check"]["status"] == 2:
                valid_usernames_list.append(username)

            request_counter += 1
            if request_counter % 2 == 0:
                time.sleep(11)

        filename = os.path.join(OUTPUTS_DIR, "valid_usernames.txt")
        with open(filename, 'w') as file:
            for username in valid_usernames_list:
                file.write(username + '\n')

        logger.success("Finished checking usernames, saved file")
        return valid_usernames_list


if __name__ == "__main__":
    checker = UsernameChecker()
    checker.check_usernames()
