from framework.core import verb
import logging

logger = logging.getLogger(__name__)


@verb
def login_page(driver, user=None, password=None, *args, **kwargs):
    """

    @param driver:
    @param user:
    @param password:
    @param args:
    @param kwargs:
    @return:
    """
    logger.info("Attempting to complete the form dialog and submit the login credentials")
    logger.info("Using {} for username".format(user))
    driver.element_find(value='username', by='name', action='send_keys', keys=[user])
    driver.element_find(by='name', value='password', action='send_keys', keys=[password])
    driver.element_find("//button[@class='radius']")

@verb
def forgot_password(driver, email, *args, **kwargs):
    """

    @param driver:
    @param email:
    @param args:
    @param kwargs:
    @return:
    """
    logger.info("Submitting {} for email address".format(email))
    driver.element_find(by='name', value='email', action='send_keys', keys=[email])
    driver.element_find("//button[@class='radius']")
