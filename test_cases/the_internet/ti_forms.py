
from test_cases.test_template import TestTemplate
from framework.the_internet.ti_core import TICore
from library.config import Config

import logging

logger = logging.getLogger(__name__)

# Loading the borg config object
config = Config()
# Loading the Core verb object for this project, TICore.
ti = TICore()


class TIForms(TestTemplate):
    """
    The class object that holds all test for project The of suite Login
    """

    def __init__(self, name):
        super(TIForms, self).__init__(name)
        # Tagging all the test_cases in this "suite" as login type test_cases
        self.doc_dict['tags'] += ['login']
        # provide shorthand overrides for test cause it's better than typing self.blah all the time
        global test
        global td
        # Get all the test date for this run
        td = ti.get_test_data()
        test = self.assertTrue

    def setUp(self):
        """
        Runs at the start of every test, some basic settings like getting the driver and what have you.
        Checks if the test is OK to run or if it should be skipped using the doc_string to determine status
        @return:
        """
        logger.info("\n" + "_" * 40 + "\nSetup")
        # Get the webdriver at the start of the test_cases
        ti.get_driver()
        logger.info("Getting Version")
        self.ok_to_run()
        self.longMessage = False
        ti.timer('start')
        logger.info("\n" + "_" * 40 + "\nTest Execution")

    def tearDown(self):
        try:
            logger.info("\n" + "_" * 40 + "\nTear Down")
            ti.timer("end")
            result = self.defaultTestResult()
            self._feedErrorsToResult(result, self._outcome.errors)
            test_result = 'passed' if len(result.failures) < 1 else 'failed'
            ti.write_result(test_result)
        except Exception as e:
            logger.exception(e)
        finally:
            ti.close_driver()