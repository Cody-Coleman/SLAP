from framework.core import verb
import logging

logger = logging.getLogger(__name__)


@verb
def authenticated(driver, *args, **kwargs):
    """

    @param driver:
    @param args:
    @param kwargs:
    @return:
    """
    logger.info("Form Submitted, Verifying results")
    driver.element_find("//h2[contains(text(), 'Secure Area')]", action=None)
    logger.info("Verifying the banner")
    driver.element_find("//div[@class='flash success']", action=None)


@verb
def not_authenticated(driver, *args, **kwargs):
    """

    @param driver:
    @param args:
    @param kwargs:
    @return:
    """
    logger.info("Form Submitted, Verifying user is not logged in")
    driver.element_find("//div[@class='flash error' and contains(text(), 'Your username is invalid!')]", action=None)
    logger.info("Found invalid user pannerbanner")


@verb
def password_sent(driver, *args, **kwargs):
    """

    @param driver:
    @param args:
    @param kwargs:
    @return:
    """
    logger.info("Form Submitted verifying that we see the email is sent message")
    driver.element_find("//div[@id='content' and contains(text(), 'been sent!')]", action=None)
    if 'email_sent' not in driver.current_url:
        raise AssertionError("URL is not correct for the email confirmation page")


@verb
def password_server_error(driver, *args, **kwargs):
    """

    @param driver:
    @param args:
    @param kwargs:
    @return:
    """
    logger.info("Verifying that with no value in the Form there is a server error")
    driver.element_find("//h1[contains(text(), 'Internal Server Error')]", action=None)
    if 'forgot_password' not in driver.current_url:
        raise AssertionError("URL is not correct for the email error page")


class Verify(object):
    def __init__(self, driver):
        self.driver = driver

    def authenticated(self, *args, **kwargs):
        """

        @param driver:
        @param args:
        @param kwargs:
        @return:
        """
        logger.info("Form Submitted, Verifying results")
        self.driver.element_find("//h2[contains(text(), 'Secure Area')]", action=None)
        logger.info("Verifying the banner")
        self.driver.element_find("//div[@class='flash success']", action=None)
        logger.info("Expected elements find")

    @verb
    def not_authenticated(self, *args, **kwargs):
        """

        @param driver:
        @param args:
        @param kwargs:
        @return:
        """
        logger.info("Form Submitted, Verifying user is not logged in")
        self.driver.element_find("//div[@class='flash error' and contains(text(), 'Your username is invalid!')]",
                            action=None)
        logger.info("Found invalid user pannerbanner")

    @verb
    def password_sent(self, *args, **kwargs):
        """

        @param driver:
        @param args:
        @param kwargs:
        @return:
        """
        logger.info("Form Submitted verifying that we see the email is sent message")
        self.driver.element_find("//div[@id='content' and contains(text(), 'been sent!')]", action=None)
        if 'email_sent' not in self.driver.current_url:
            raise AssertionError("URL is not correct for the email confirmation page")

    @verb
    def password_server_error(self, *args, **kwargs):
        """

        @param driver:
        @param args:
        @param kwargs:
        @return:
        """
        logger.info("Verifying that with no value in the Form there is a server error")
        self.driver.element_find("//h1[contains(text(), 'Internal Server Error')]", action=None)
        if 'forgot_password' not in self.driver.current_url:
            raise AssertionError("URL is not correct for the email error page")
