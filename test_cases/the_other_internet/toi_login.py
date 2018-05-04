
from test_cases.test_template import TestTemplate
from framework.the_internet.ti_core import TICore
from library.config import Config

import logging

logger = logging.getLogger(__name__)

# Loading the borg config object
config = Config()
# Loading the Core verb object for this project, TICore.
ti = TICore()


class TOILogin(TestTemplate):
    """
    The class object that holds all test for project The of suite Login
    """

    def __init__(self, name):
        super(TOILogin, self).__init__(name)
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

    def test_toi_login_0001(self):
        """
        Login: Login using form
        @test Attempt login using a webform and submitting username and pass
        @author CodyC
        @date 04/29/18
        """
        # DEMONSTRATES NAVIGATING TO A LOGIN PAGE, WITH CUSTOM ERROR MESSAGES
        try:
            # NAVIGATE TO THE PAGE
            test(ti.go_to(location="The Internet", url=td.url), "Failed to navigate to the starting page")
            # OPEN THE POPUP DIALOG
            test(ti.go_to(location="Form Authentication"), "Failed to navigate to the form authentication page")
            # FILL OUT THE FORM
            test(ti.dialog(dialog='Login Page', user=td.user, password=td.password), "Failed to fill out the form")
            # VERIFY THE RESULTS OF THE LOGIN
            test(ti.verify(item="Authenticated"), "Failed to Authenticate")
        except Exception as e:
            ti.write(e, level='error')
            ti.take_screenshot(self.whoami())
            # self.fail(e)
        finally:
            logger.info("\n" + "_" * 40 + "\nFinally")

    def test_toi_login_0002(self):
        """
        Login: Failed login test, expected to fail
        @test Uses bad credentials to login, test is an example of a failure
        @author CodyC
        @date 04/29/18
        """
        # DEMONSTRATES NAVIGATING TO A LOGIN PAGE, WITH ERROR CODES FOR FAILURES AND CUSTOM ERRORS
        try:
            # NAVIGATE TO THE PAGE
            test(ti.go_to(location="The Internet", url=td.url), "GOTO_0000")
            # OPEN THE POPUP DIALOG
            test(ti.go_to(location="Form Authentication"), "GOTO_0001")
            # FILL OUT THE FORM
            test(ti.dialog(dialog='Login Page', user=td.bad_user, password=td.bad_pass), "DIALOG_0001")
            # VERIFY THE RESULTS OF THE LOGIN
            test(ti.verify(item="Authenticated"), "Failed to Authenticate")
        except Exception as e:
            ti.write(e, level='error')
            ti.take_screenshot(self.whoami())
            self.fail(e)
        finally:
            logger.info("\n" + "_" * 40 + "\nFinally")

    def test_toi_login_0003(self):
        """
        Login: Failed login test
        @test Uses bad credentials to login, and looks for failure dialog
        @author CodyC
        @date 04/29/18
        """
        # DEMONSTRATES NAVIGATING TO A LOGIN PAGE, WITH ERROR CODES FOR FAILURES
        try:
            # NAVIGATE TO THE PAGE
            test(ti.go_to(location="The Internet", url=td.url), "GOTO_0000")
            # OPEN THE POPUP DIALOG
            test(ti.go_to(location="Form Authentication"), "GOTO_0001")
            # FILL OUT THE FORM
            test(ti.dialog(dialog='Login Page', user=td.bad_user, password=td.bad_pass), "DIALOG_0001")
            # VERIFY THE RESULTS OF THE LOGIN
            test(ti.verify(item="Not Authenticated"), "VERIFY_0003")
        except Exception as e:
            ti.write(e, level='error')
            ti.take_screenshot(self.whoami())
            self.fail(e)
        finally:
            logger.info("\n" + "_" * 40 + "\nFinally")

    def test_toi_login_0004(self):
        """
        Login: Forgot Password
        @test Submit form to get an eamil
        @author CodyC
        @date 04/29/18
        """
        # DEMONSTRATES NAVIGATING TO A ANOTHER FORM PAGE, WITH ERROR CODES FOR FAILURES
        try:
            # NAVIGATE TO THE PAGE
            test(ti.go_to(location="The Internet", url=td.url), "GOTO_0000")
            # OPEN THE POPUP DIALOG
            test(ti.go_to(location="Forgot Password"), "GOTO_0001")
            # FILL OUT THE FORM
            test(ti.dialog(dialog='Forgot Password', email=td.email), "DIALOG_0001")
            # VERIFY THE RESULTS OF THE LOGIN
            test(ti.verify(item="Password Sent"), "VERIFY_0000")
        except Exception as e:
            ti.write(e, level='error')
            ti.take_screenshot(self.whoami())
            self.fail(e)
        finally:
            logger.info("\n" + "_" * 40 + "\nFinally")

    def test_toi_login_0005(self):
        """
        Login: Forgot Password, Invalid value
        @test Submit form with no value in the email box, expect to get an error message
        @author CodyC
        @date 04/29/18
        """
        # DEMONSTRATES NAVIGATING TO A ANOTHER FORM PAGE, WITH SHORTHAND PARAMETERS, AND CUSTOM TEST DATA
        try:
            # NAVIGATE TO THE PAGE
            test(ti.go_to("The Internet", url=td.url), "GOTO_0000")
            # OPEN THE POPUP DIALOG
            test(ti.go_to("Forgot Password"), "GOTO_0001")
            # FILL OUT THE FORM
            test(ti.dialog('Forgot Password', email=''), "DIALOG_0001")
            # VERIFY THE RESULTS OF THE LOGIN
            test(ti.verify("Password Server Error"), "VERIFY_0000")
        except Exception as e:
            ti.write(e, level='error')
            ti.take_screenshot(self.whoami())
            self.fail(e)
        finally:
            logger.info("\n" + "_" * 40 + "\nFinally")

