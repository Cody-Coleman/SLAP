import yaml
import logging
import fnmatch
import os

from box import Box, BoxKeyError

logger = logging.getLogger(__name__)


class TestData(Box):
    def __getattr__(self, item):
        try:
            return Box.__getattr__(self, item)
        except BoxKeyError:
            return None


def map_yaml(directory, exclusion, environment):
    """
    parses through all the yaml files in the assets directory creating a multi-level dictionary object
    @param string directory: where to start looking for all the test data
    @param list exclusion: a list of files to exclude from the test data load
    @param environment: The datacenters this test run is in, and the test data to pull
    @note This only allows a single level mapping, no deeper. In almost all cases when trying to go deeper, you should
    just re-work the test data
    @return: Test Data dictionary object
    """
    test_data = {}

    for root, dirnames, filenames in os.walk(directory):
        for filename in fnmatch.filter(filenames, '*.yaml'):
            if filename not in exclusion:
                tmp_config = yaml.load(open(os.path.join(root, filename), 'rb').read())
                if 'environment' in tmp_config['test_data'] and tmp_config['test_data'][
                    'environment'] == environment:
                    test_data.update(tmp_config['test_data'])

    logger.info("Loaded {} configs".format(len(test_data)))
    return TestData(test_data)
