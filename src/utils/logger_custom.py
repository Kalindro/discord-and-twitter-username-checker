import os
import sys

from loguru import logger

from src.utils.dir_paths import LOG_DIR


class LoggerCustom:
    """My custom logger, used for default and customized level logging"""

    def __init__(self):
        self.custom_format = ("<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                              "<level>{level: <9}</level>| "
                              "<level>{message: <45}</level> | "
                              "<blue>{function}</blue> | "
                              "<magenta>{file}:{line}</magenta>")

    def info_level(self):
        return self._level_config(level="INFO")

    def debug_level(self):
        return self._level_config(level="DEBUG")

    def error_level(self):
        return self._level_config(level="ERROR")

    def info_only(self):
        return self._level_only_config(level="INFO")

    def debug_only(self):
        return self._level_only_config(level="DEBUG")

    def error_only(self):
        return self._level_only_config(level="ERROR")

    def _level_config(self, level):
        custom_logger = self._basic_config()
        custom_logger.add(sink=sys.stderr, level=level, format=self.custom_format)
        return custom_logger

    def _level_only_config(self, level):
        custom_logger = self._basic_config()

        def _log_level_filter(record):
            return record["level"].name == level

        custom_logger.add(sink=sys.stderr, level=level, format=self.custom_format, filter=_log_level_filter)
        return custom_logger

    def _basic_config(self):
        logger.remove()
        logs_path = os.path.join(LOG_DIR, "errors.log")
        logger.add(sink=logs_path, level="ERROR", format=self.custom_format)
        return logger


default_logger = LoggerCustom().info_level()
