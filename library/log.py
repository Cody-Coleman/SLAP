'''
Created on Dec 19, 2012

@author: cody.coleman
'''

import logging
import os

debug_formatter = logging.Formatter("%(asctime)s - [%(uuid)s: %(levelname)s] - [%(name)s:%(lineno)d] - %(message)s",
                                    "%m-%d %H:%M:%S")

standard_formatter = logging.Formatter("%(asctime)s - [%(levelname)s] -  %(message)s",
                                       "%m-%d %H:%M:%S")


class InjectUUID(logging.Filter):
    def __init__(self, uuid):
        self.uuid = uuid

    def filter(self, record):
        record.uuid = self.uuid
        return True


def log_init(level, path, uuid):
    """
    Initialize logging for starforge
    Args:
        level (int): What level to use for logging.
        path (string): Where to write the file to
        uuid (string): Unique ID for the run
    """
    log_levels = {
        1: logging.INFO,
        0: logging.DEBUG,
        2: logging.WARNING,
        3: logging.ERROR,
        4: logging.CRITICAL
    }
    root_logger = logging.getLogger()
    # KILL THE VERBOSITY OF REQUESTS LOGGING
    logging.getLogger('requests').setLevel(logging.ERROR)
    logging.getLogger('urllib3').setLevel(logging.ERROR)
    logging.getLogger('boto').setLevel(logging.ERROR)
    logging.getLogger('selenium').setLevel(logging.ERROR)

    # GET GLOBAL LOGGER
    root_logger.setLevel(logging.DEBUG)
    s_handler = logging.StreamHandler()
    s_handler.setLevel(log_levels[level])
    s_handler.addFilter(InjectUUID(uuid))

    if log_levels[level] == logging.DEBUG:
        s_handler.setFormatter(debug_formatter)
    else:
        s_handler.setFormatter(standard_formatter)
    root_logger.addHandler(s_handler)
    # log_to_file(path, root_logger, uuid)


def log_to_file(full_path, root_logger, uuid):
    """
    Enabled debug logs to disk
    Args:
        full_path (string): The full path to the file
        root_logger (Logger): object to use the logger
        uuid (string): unique id used for formatting.
    """
    root_logger = logging.getLogger()
    file_dir, file_name = os.path.split(full_path)
    if file_dir is not None:
        if not os.path.isdir(file_dir):
            os.makedirs(file_dir)
    log_file_handler = logging.FileHandler(full_path)
    log_file_handler.setLevel(logging.DEBUG)
    log_file_handler.setFormatter(debug_formatter)
    log_file_handler.addFilter(InjectUUID(uuid))
    root_logger.addHandler(log_file_handler)
