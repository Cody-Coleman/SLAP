from framework.core import verb
import logging

logger = logging.getLogger(__name__)


@verb
def the_internet(driver, url=None, *args, **kwargs):
    """

    @param driver:
    @param url:
    @param args:
    @param kwargs:
    @return:
    """
    driver.get(url)
    driver.element_find("//h1[text()='Welcome to the-internet']", action=None)


@verb
def form_authentication(driver):
    """

    @param driver:
    @return:
    """
    logger.info("Clicking Form Autentication Page")
    driver.element_find("//a[text()='Form Authentication']")
    # Verify we are on the auth page
    driver.element_find("//h2[text()='Login Page']", action=None)
    if 'login' not in driver.current_url:
        raise AssertionError("Expected to find Login in page URL")


@verb
def forgot_password(driver):
    """

    @param driver:
    @return:
    """
    logger.info("Navigating to the 'Forgot Password' form")
    driver.element_find("//a[text()='Forgot Password']")
    logger.info("Verifying we navigated correctly")
    driver.element_find("//h2[text()='Forgot Password']", action=None)
    if 'forgot_password' not in driver.current_url:
        raise AssertionError("Expected to find forgot_password in Page URL")
