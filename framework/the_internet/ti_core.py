from framework.core import Core
from time import sleep
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotVisibleException
from library.config import Config

from framework.the_internet.verify import Verify
import logging


logger = logging.getLogger(__name__)
config = Config()


class TICore(Core):
    def __init__(self):
        """
        @return Verb Object
        @note sets self.driver to None
        """
        super(TICore, self).__init__()
        self.verify_obj = Verify(self.driver)

    def go_to(self, location, menu=None, *args, **kw):
        """
            Go To verb that calls go_to for all navigation actions
            @param location (string) - Location is a major category that contains the menu item
            @param menu (string) - Menu is the sub-string location that is grouped by location,
            this is only needed for the go_to
            @param args (arguments) - Variable list of args possibly needed for the go_to sub function
            @param kw (hash arguments) - Variable list of key=value arguments possibly needed for the go_to sub function
            @return bool - True if all works, false if anything fails
            @note Verb will fail if the elements are not on the page, or if a call to an undefined location/menu is used
                   Also note that menu is optional, some locations are just locations.
            @par EXAMPLE:
            test(tic.go_to(location='Actions', menu='Products'))
            @par
            test(tic.go_to(location='Button', text='OK'))
        """
        try:
            logger.info("Trying Location %s and Menu %s" % (location, menu))
            # Sanitize the Go_To
            location = self.sanitize(location)
            if menu is not None:
                menu = self.sanitize(menu)
                location = "{}_{}".format(location, menu)
            logger.debug("Using [{}] for Location".format(location))
            # Import the go_to library, find the function then call it
            import framework.the_internet.go_to
            func = getattr(framework.the_internet.go_to, location)
            logger.debug("\n{}\n".format(func.__doc__))
            func(self.driver, *args, **kw)
            sleep(1)
            return True

        except AttributeError as e:
            logger.error("Failed to find go_to submodule\n{}".format(str(e)))
            return False
        except TimeoutException as e:
            logger.error("Timed Out waiting for page to load or element to be found: {}".format(str(e)))
            return False
        except NoSuchElementException as e:
            logger.error("Failed to find element {}".format(str(e)))
            return False
        except ElementNotVisibleException as e:
            logger.error("Element is not visible, so cannot be clicked: {}".format(str(e)))
            return False
        except Exception as e:
            logger.error("Unhandled exception: {} ".format(str(e)))
            return False

    def dialog(self, dialog, *args, **kw):
        """
            Verb that handles all calls dealing with an any kind of dialog popup or form fields
            @param dialog (string) - The dialog class  form that will be filled out
            @param args (arguments) - Variable list of args possibly needed for the go_to sub function
            @param kw (hash arguments) - Variable list of key=value arguments possibly needed for the go_to sub function
            @return bool - True if all works, false if anything fails
            @note Verb will fail if the call to an invalid action is used,
            check the documentation for what actions are supported
            @par EXAMPLE:
            self.assertTrue(ts.assessment(action='Select Assessment Drop Down'), "A0001")
        """
        try:
            logger.info("Trying Dailog {}".format(dialog))
            # SANITIZE ACTION
            dialog = self.sanitize(dialog)
            logger.debug("Using sanitized [{}]".format(dialog))
            # Import the assessment library, find the function then call it
            import framework.the_internet.dialog
            func = getattr(framework.the_internet.dialog, dialog)
            logger.debug("\n{}\n".format(func.__doc__))
            func(self.driver, *args, **kw)
            sleep(0.5)
            return True
        except AttributeError as e:
            logger.error("Failed to find dialog submodule\n{}".format(str(e)))
            return False
        except TimeoutException as e:
            logger.error("Timed Out waiting for page to load or element to be found: {}".format(str(e)))
            return False
        except NoSuchElementException as e:
            logger.error("Failed to find element {}".format(str(e)))
            return False
        except Exception as e:
            logger.error("Unhandled exception: {} ".format(str(e)))
            return False

    def verify(self, item, *args, **kw):
        """
            Calls the underlying verify sub verbs
            @param item (string) - The item to verify
            @param args (Variable positions arguments) - holds any position arguments
            @param kw (Variable Dictionary) - A variable dictionary that holds optional parameters
            @par EXAMPLE
            self.assertTrue(ts.verify(item='Subject Report', name=td.assessment_one), "V0001")
        """
        try:
            if item is None:
                raise AssertionError("Didn't pass in the Item to evaluate")
            logger.info("Attempting to verify {}".format(item))
            item = self.sanitize(item)
            logger.debug("Using [{}] for item".format(item))
            import framework.the_internet.verify
            func = getattr(framework.the_internet.verify, item)
            logger.debug("\n{}\n".format(func.__doc__))
            func(self.driver, *args, **kw)
            sleep(0.5)
            return True
        except AttributeError as e:
            logger.error("Error with Attribute when calling submodule\n{}".format(str(e)))
            return False
        except TimeoutException as e:
            logger.error("Timed Out waiting for page to load or element to be found: {}".format(str(e)))
            return False
        except ElementNotVisibleException as e:
            logger.error("Element is not visible, so cannot be clicked: {}".format(str(e)))
            return False
        except AssertionError as e:
            logger.error("Assertion Error: {}".format(str(e)))
            return False
        except Exception as e:
            logger.error("Unhandled exception: {} ".format(str(e)))
            return False
