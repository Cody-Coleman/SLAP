## @package framework.driver
#  This is the main holding area for anything related to Selenium WebDriver functionality
import functools
import json
import os
from time import sleep, time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from library.config import Config


import logging

logger = logging.getLogger(__name__)


class Driver(webdriver.Chrome, webdriver.Ie, webdriver.Firefox):
    """
        Overloaded WebDriver class, was needed to provide a simpler method of calling the element_find. 
        However it can be a bit brittle if the web drivers ever change their close method... mostly due to
        How chrome doesn't just quit, but needs to close then quit, where as firefox and ie need to only close and 
        have no quit
    """

    def __init__(self, browser_type, device_type=None, *args, **kw):
        # from framework.core import Core
        from library.helper import file_path
        config = Config()
        self.browser_type = browser_type.lower()
        if device_type:
            self.device_type = device_type.lower()
        download_path = config['log_dir']
        config['download_dir'] = download_path
        if self.browser_type in ('firefox', 'mobile'):
            profile = webdriver.FirefoxProfile()
            profile.set_preference("browser.download.folderList", 2)
            profile.set_preference('browser.download.manager.showWhenStarting', False)
            profile.set_preference('browser.helperApps.alwaysAsk.force', False)
            profile.set_preference('browser.helperApps.neverAsk.saveToDisk', (
            'application/octet-stream,application/x-pdf,application/vnd.pdf,application/vnd.msexcel,application/zip,application/pdf,application/vnd.openxmlformats-officedocument.word,application/x-spss,application/x-spss-sav,application/spss-sav,application/x-unknown-content-type,text/php,text/csv,application/json,text/xml,text/html'))
            profile.set_preference("plugin.disable_full_page_plugin_for_types", "application/pdf")
            profile.set_preference("pdfjs.disabled", True)
            profile.set_preference("browser.download.dir", download_path)
            profile.set_preference("devtools.selfxss.count", 11)
            profile.set_preference("print.always_print_silent", True)
            ext = file_path("PUP Network Listener.xpi")
            profile.add_extension(ext)

            if device_type == 'iphone':
                profile.set_preference("general.useragent.override",
                                       "Mozilla/5.0 (iPhone; CPU iPhone OS 8_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) FxiOS/1.0 Mobile/12F69 Safari/600.1.4")
            elif device_type == 'ipad':
                profile.set_preference("general.useragent.override",
                                       "Mozilla/5.0 (iPad; CPU iPhone OS 8_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) FxiOS/1.0 Mobile/12F69 Safari/600.1.4")
            elif device_type == 'ipod':
                profile.set_preference("general.useragent.override",
                                       "Mozilla/5.0 (iPod touch; CPU iPhone OS 8_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) FxiOS/1.0 Mobile/12F69 Safari/600.1.4")
            elif device_type == 'android':
                profile.set_preference("general.useragent.override",
                                       "Mozilla/5.0 (Android; Mobile; rv:40.0) Gecko/40.0 Firefox/40.0")

            if self.browser_type == 'mobile':
                profile.set_preference("devtools.responsiveUI.currentPreset", "custom")
                profile.set_preference("dom.w3c_touch_events.enabled", 1)
                profile.set_preference("devtools.responsiveUI.customHeight", 640)
                profile.set_preference("devtools.responsiveUI.customWidth", 360)

                ext = file_path("MobileEnable.xpi")
                profile.add_extension(ext)

            self = webdriver.Firefox.__init__(self, firefox_profile=profile, *args, **kw)

        elif self.browser_type == 'chrome':
            options = webdriver.ChromeOptions()
            options.add_argument('test-type')
            options.add_argument('disable-popup-blocking')

            ext = file_path("PUP Network Listener.crx")
            options.add_extension(ext)

            prefs = {"download.default_directory": download_path}
            options.add_experimental_option("prefs", prefs)
            import platform
            os_name = platform.system()
            if os_name == 'Windows':
                service_args = ['--log-path=NUL']
            else:
                service_args = ['--verbose', '--log-path=/dev/null']
            service_args.append('--disable-print-preview')

            if device_type == 'iphone':
                user_agent = "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_0 like Mac OS X; en) AppleWebKit/534.46.0 (KHTML, like Gecko) CriOS/19.0.1084.60 Mobile/9B206 Safari/7534.48.3"
                options.add_argument("user-agent=" + user_agent)
            elif device_type == 'ipad':
                user_agent = "Mozilla/5.0 (iPad; U; CPU OS 4_3 like Mac OS X; en) AppleWebKit/534.46.0 (KHTML, like Gecko) CriOS/19.0.1084.60 Mobile/9B206 Safari/7534.48.3"
                options.add_argument("user-agent=" + user_agent)
            elif device_type == 'android':
                user_agent = "Mozilla/5.0 (Linux; Android 5.0.2; SM-G901F Build/LRX22G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Mobile Safari/537.36"
                options.add_argument("user-agent=" + user_agent)

            self = webdriver.Chrome.__init__(self, chrome_options=options, service_args=service_args, *args, **kw)

        elif self.browser_type == 'ie':
            self = webdriver.Ie.__init__(self, *args, **kw)
        elif self.browser_type == 'ghost':
            self.session_id = ""
            pass
        elif self.browser_type == 'vanilla':
            self = webdriver.Firefox.__init__(self, *args, **kw)
        else:
            raise AttributeError("Browser Type [{}] Unknown".format(browser_type))

    def accept_alert(self):
        """
            Confirm the browser alert
            @author Jaysen
            @date 8/1/13
            @par EXAMPLE: rs_core.confirm_alert()
        """
        Alert(self).accept()

    def close_driver(self):
        """
            Closes the Driver depending on the type of WebDriver
            @note Only Chrome needs an additional step to close, order is significant
        """
        if self.browser_type == 'firefox':
            windows = self.window_handles
            for window in windows:
                self.switch_to.window(window)  # pylint: disable=no-member
                webdriver.Firefox.close(self)
        elif self.browser_type == 'ie':
            webdriver.Ie.quit(self)
        elif self.browser_type == 'chrome':
            webdriver.Chrome.close(self)
            webdriver.Chrome.quit(self)
        elif self.browser_type == 'ghost':
            logger.debug("Skipping close step for ghost driver")
        else:
            self.quit()
        from selenium.webdriver.support import expected_conditions as ec
        try:
            WebDriverWait(self, 5).until(ec.alert_is_present())
            self.switch_to.alert.accept()  # pylint: disable=no-member
        except:
            pass

    def close_page(self):
        """
            Need a way to close just the tab/popup window
        """
        self.close()

    def element_find(self, value='', by='xpath',
                     action='click', keys=[], index=0,
                     wait=10, element=None, fail=False,
                     return_list=False, target=None,
                     x=None, y=None, modifier_key=None, logs=True):
        """
            Find the element at Xpath and perform action 
            @param    value (string) - The string value of the xpath to use in the search
            @param    by (string) - The type of action to perform, click or send_keys
            @param    action (string) - The type of action to perform, such as click, send_keys, clear, or none
            @param    keys (list, or Keys ENUM) - The keys to send or a Key ENUM such as ENTER or ARROW_UP
            @param    index (int) - The index of elements to select, since this always finds a list
            @param    wait (float) - The amount of time to wait for the element to be found
            @param    element (WebElement) - If passed, will use that element for the searches
            @param    fail (bool) - If set, element_find does not expect to find the element, and that is ok
            @param    return_list (bool) - Specifies whether or not to return as a list
            @param    target (WebElement) - Specifies where to drop an element that is being dragged
            @param    x (float) - The X parameter used if you use click_at
            @param    y (float) - The y parameter used if you use click_at
            @param    modifier_key (string) - the modifier key to hold while clicking ("control", "command", etc.)
            @param    logs (bool) - If False, will not log the debug statements
            (for situations like element_gone that would spam the logs)
            @return   WebDriver Element
        """
        by = self.sanitize(by)
        if logs:
            logger.debug("using by_%s to find element [%s]" % (by, value))
        # Will Try to find the element, which the element may not need to be found
        w_object = self
        if element is not None:
            w_object = element
        try:
            if by == 'class_name':
                element = WebDriverWait(w_object,
                                        wait).until(lambda driver: w_object.find_elements_by_class_name(value))
            elif by == 'css_selector':
                element = WebDriverWait(w_object,
                                        wait).until(lambda driver: w_object.find_elements_by_css_selector(value))
            elif by == 'id':
                element = WebDriverWait(w_object,
                                        wait).until(lambda driver: w_object.find_elements_by_id(value))
            elif by == 'link_text':
                element = WebDriverWait(w_object,
                                        wait).until(lambda driver: w_object.find_elements_by_link_text(value))
            elif by == 'partial_link_text':
                element = WebDriverWait(w_object,
                                        wait).until(lambda driver: w_object.find_elements_by_partial_link_text(value))
            elif by == 'name':
                element = WebDriverWait(w_object,
                                        wait).until(lambda driver: w_object.find_elements_by_name(value))
            elif by == 'tag':
                element = WebDriverWait(w_object,
                                        wait).until(lambda driver: w_object.find_elements_by_tag_name(value))
            elif by == 'xpath':
                element = WebDriverWait(w_object,
                                        wait).until(lambda driver: w_object.find_elements_by_xpath(value))
        except Exception:
            # If fail is false, then not finding the element is unexpected
            if return_list:
                return []
            if not fail:
                raise TimeoutException("Value: %s, by: %s, wait: %s" % (value, by, wait))
            elif fail:
                return
        # If fail is set and we found the element, this has failed, as the element was not supposed to be there
        if fail:
            raise TimeoutException("Value: %s, by: %s, wait: %s" % (value, by, wait))
        # Found the element, now to sanitize the action and perform it
        # Note... none isn't an action, but wont match the if-elsif so is the default behavior of do nothing
        # Technically anything could get passed in that wasn't click, send_keys or clear and it will do nothing
        if logs:
            logger.debug("Found %d number of elements" % (len(element)))
        if return_list:
            return element

        action_chain = None
        # sanitize action
        if action is not None:
            action = self.sanitize(action)
            action_chain = ActionChains(self)

            if modifier_key:
                modifier_key = [modifier_key] if type(modifier_key) is not list else modifier_key
                for k in modifier_key:
                    action_chain.key_down(self.sanitize_modifier_key(k))

        # Click does not work with modifier keys, use click_action
        if action == 'click' and len(keys) == 0:
            element[index].click()
        # Use click action if you need to because you need the click in the correct place
        # in the action chain (because of modifier keys, etc.)
        elif action == 'click_action':
            action_chain.click(element[index])
        # FIREFOX DOESN'T WORK WITH CLICK_AT
        elif action == "click_at":
            action_chain.move_to_element_with_offset(element[index], x, y).click()
        elif action == 'click_and_hold':
            action_chain.click_and_hold(element[index]).release(element[index])
        elif action == "double_click":
            action_chain.double_click(element[index])
        elif action == "right_click":
            action_chain.context_click(element[index])
        elif action == "drag_and_drop":
            action_chain.drag_and_drop(element[index], target)
        elif action == "drag_and_drop_by_offset":
            action_chain.drag_and_drop_by_offset(element[index], x, y)
        elif action == 'move_to_element':
            action_chain.move_to_element(element[index]).click()
        elif action == 'hover' or action == 'mouse_in':
            action_chain.move_to_element(element[index])
        elif action == 'send_keys':
            for val in keys:
                try:
                    logger.debug("sending [%s] to element" % value)
                    element[index].send_keys(val.decode('utf8'))
                except (UnicodeEncodeError, AttributeError):
                    element[index].send_keys(val)
                if len(keys) > 1 and not isinstance(keys, str):
                    sleep(0.1)
        elif action == 'clear':
            logger.debug("Clearing field")
            element[index].clear()
        elif action == 'select':
            element._setSelected()

        if action:
            if modifier_key:
                for k in modifier_key:
                    action_chain.key_up(self.sanitize_modifier_key(k))
            action_chain.perform()

        # ADDING THE ABILITY TO USE KEYS AFTER action == 'clear'
        if len(keys) > 0 and action != 'send_keys':
            for val in keys:
                try:
                    logger.debug("sending [%s] to element" % value)
                    element[index].send_keys(val.decode('utf8'))
                except (UnicodeEncodeError, AttributeError):
                    element[index].send_keys(val)
                if len(keys) > 1 and not isinstance(keys, str):
                    sleep(0.1)
        return element[index]

    def element_gone(self, value='', by='xpath', wait=10, find_first=False):
        """
            waits for the element to no longer be found by value 
            @param value (string) - The id, name, xpath, or css to search for
            @param by (string) - Takes the same values as element_find, xpath, id, name, class, etc
            @param wait (int) - How long to wait for the element to no longer be found. And if find_first waits this amount of time
            @param find_first (bool) - Whether or not to first find the element
            @throws TimeoutException - will raise if timeout expires and the element is still found
            @author Cody C
            @date 8/3/13
            @par EXAMPLE
            driver.element_gone("//input[@id='confirmationInput']", wait=10, by='xpath') 
        """
        if find_first:
            logger.debug("Waiting for element to appear before waiting for it to be gone")
            self.element_find(value=value, by=by, wait=wait, action='')
        logger.debug("Waiting for element to clear")
        logger.debug("Value=%s" % value)
        logger.debug("Searching for element by %s" % by)
        logger.debug("For %d seconds" % wait)
        start = time()
        found = True
        while time() - start < wait:
            try:
                self.element_find(value, by, action='None', wait=0.1, logs=False)
            except TimeoutException:
                logger.debug("Element no longer found")
                logger.debug("Took %d seconds" % (time() - start))
                found = False
                break
            except StaleElementReferenceException:
                logger.debug("There was a StaleElementReferenceException")
                found = False
                break
        if found:
            raise TimeoutException("Element still found: [%s] by [%s]" % (value, by))
        else:
            return True

    def execute_script(self, script, retry=True, silent=False, *args):
        """
            instead of throwing an exception, handles and returns None instead
        """

        logger.debug("Executing Script: %s" % script)
        try:
            return super(Driver, self).execute_script(script, *args)
        except Exception as e:
            if silent:
                logger.debug("JS Exception: %s" % str(e))
            else:
                logger.error("JS Exception: %s" % str(e))
            if retry:
                sleep(1)
                logger.debug("Attempting to repeat script")
                self.execute_script(script, retry=False, silent=silent, *args)
            return None

    def js_snippet(self, snippet_title, format_text=None, *args):
        """ 
            Runs a javascript snippet
            @param snippet_title (string) - the name of the snippet to execute
            @param format_text (string) -
            @param args (Variable arguments) - the arguments to pass into the execute script
            @returns the return value of the javascript snippet
        """
        config = Config()
        logger.debug("Snippet: {} beginning...".format(snippet_title))
        # Read in the JSSnippet
        script = ""
        snippet_path = config['js_snippet_dir']
        with open(os.path.join(snippet_path, snippet_title), 'r') as f:
            script += f.read()
        if format_text is not None:
            script = script % format_text
        ret_val = self.execute_script(script, True, False, *args)
        logger.debug("Snippet: {} complete...".format(snippet_title))
        return ret_val

    def js_errors(self):
        """
            Gets all uncaught javascript errors thrown since js_listener was called
            @returns a list of errors: {msg, url, line_number}
        """
        ret_val = json.loads(self.js_snippet('getErrors.js'))
        logger.debug('The following JS Errors were read: {}'.format(ret_val))
        return ret_val

    def wait_for_no_requests(self, timeout=None, wait=None, fail_on_timeout=False):
        """
            Waits for no more Ajax requests on the page before return
            @author Cameron Holiman
            @param timeout (int) - the time in seconds to wait for requests to finish before exiting
            @param wait (int) - the time to wait after all AJAX requests finish before assuming no more will be made
            @param fail_on_timeout (boolean) - if True, an exception will be thrown if the timeout happens
            @par EXAMPLE
            driver.wait_for_no_requests(timeout=10, wait=.5, fail_on_timeout=True)
        """
        timeout = timeout if timeout else 20

        wait = wait if wait else 0
        last_ajax_time = time()
        ajax_timer_started = False
        start_time = time()
        logger.debug("waiting for AJAX to finish")
        while time() < start_time + timeout:
            # if no more know ajax requests on page
            # IF (PUP network listener exists, use that to get the requests. Else if Ajax is on the page and it has an
            # active request count, use that. Else just return 0
            if self.execute_script("return window.hasOwnProperty('PUPNetworkListener') ? "
                                   "PUPNetworkListener.getActiveRequestCount() : "
                                   "(window.hasOwnProperty('Ajax') && Ajax.hasOwnProperty('activeRequestCount')) ? "
                                   "Ajax.activeRequestCount : 0") == 0:
                if ajax_timer_started is False:
                    logger.debug("no more AJAX found, starting timer")
                    last_ajax_time = time()
                    ajax_timer_started = True

                if time() > last_ajax_time + wait:
                    logger.debug("No more AJAX found after {}s, breaking out".format(timeout))
                    break
            else:
                ajax_timer_started = False

            sleep(.1)

        if ajax_timer_started is False:
            logger.debug("AJAX timed out after {}s".format(timeout))
            if fail_on_timeout is True:
                assert TimeoutException(
                    self.execute_script("return window.hasOwnProperty('Ajax') ? Ajax.activeRequestCount : 0")) == 0, \
                    "The AJAX on the page never returned"

    @staticmethod
    def sanitize(str_value):
        """
            Sanitize a string in order to make it easy to work with by removing leading or trailing
            whitespace, and replacing spaces in between the words with an underscore (_) as well
            @param str_value (string) - String to sanitize
            @return string
        """
        if not str_value:
            return str_value
        value = ((str_value.strip()).replace(' ', '_')).lower()
        # logger.debug("sanitized [%s] to [%s]" %(str_value, value))
        return value

    @staticmethod
    def sanitize_modifier_key(str_key):
        """
            Takes a string representation of a modifier key and returns the selenium Key for it.
            If the key is not recognized, it will return the input string
            @param str_key
        """
        if type(str_key) is str:
            keys = {"ctrl": Keys.CONTROL,
                    "control": Keys.CONTROL,
                    "alt": Keys.ALT,
                    "option": Keys.ALT,
                    "cmd": Keys.COMMAND,
                    "command": Keys.COMMAND,
                    "shift": Keys.SHIFT}

            return keys[str_key.lower()]
        return str_key

    def wait_for_text(self, value='', by='xpath', current_text='', wait=10, ignore=False):
        """
            Waits for the element to have a text value before continuing 
            @param value (string) - The string value of the xpath to use in the search
            @param by (string) - The type of action to perform, click or send_keys
            @param current_text (string) - What the current text is that we are waiting on to change 
            @param wait (int) - How long to wait for the text to show up
            @param ignore (bool) - If true will ignore the fact the text never changed,
            if false will expect text to load
            @throws NoSuchElementException if text attribute is still empty
            @author CodyC
            @date 8/3/13
            @par EXAMPLE
            driver.wait_for_text("//input[contains(@id,"FirstNameField")]", by="xpath")
        """
        logger.info("Waiting for Field to populate with text")
        start = time()
        el = self.element_find(value, by, action="None")
        while el.get_attribute("value") == current_text:
            if time() - start > wait:
                break
            else:
                el = self.element_find(value, by, action="None")
        logger.info("Checking if value of input is not empty (expects not to be empty)")
        el = self.element_find(value, by, action="None")
        if el.get_attribute("value") == current_text:
            if ignore:
                logger.error("Text never changed")
            else:
                raise NoSuchElementException("input field is %s, expecting it to change" % current_text)


class JSListener(object):
    """ Decorator. Injects javascript into a page to track js errors on page """
    raise_on_js_error = None

    def __init__(self, func):
        self.func = func

    def __get__(self, instance, instancetype):
        """Implement the descriptor protocol to make decorating instance method possible."""

        # Return a partial function with the first argument is the instance 
        #   of the class decorated.
        return functools.partial(self.__call__, instance)

    def __call__(self, *args, **kw):
        return self.listener(self.func)

    @classmethod
    def listener(self, func):
        def wrap(*args, **kw):

            # Check config
            if self.raise_on_js_error is None:
                self.get_config()

            # Get Driver
            driver = None
            if len(args) > 0 and type(args[0]) is Driver:
                driver = args[0]
            elif 'driver' in kw:
                driver = kw['driver']

            # Get Raise on js error
            raise_on_js_error = self.raise_on_js_error
            if 'raise_on_js_error' in kw:
                raise_on_js_error = kw['raise_on_js_error']

            # Add Listener
            if driver is not None:
                logger.debug('Listening To js errors')
                driver.js_snippet('addErrorListener.js')

            # Invoke the wrapped function
            retval = func(*args, **kw)

            if driver is not None:
                try:
                    js_errors = driver.js_errors()
                except:
                    js_errors = []
                for e in js_errors:
                    msg = 'JS ERROR - MESSAGE {} - LINE {} - URL {}'.format(
                        e['msg'], e['linenumber'], e['url'])
                    logger.error(msg)

                if len(js_errors) > 0 and raise_on_js_error:
                    raise WebDriverException('Javascript Errors')
            return retval

        return wrap

    @classmethod
    def get_config(self):

        # Get the global config value for raise on js error
        from framework.core import Core
        core = Core()
        raise_on_js_error = core.get_config_value('RAISE_ON_JS_ERROR')
        if raise_on_js_error is None or raise_on_js_error.lower() == 'false':
            raise_on_js_error = False
        else:
            raise_on_js_error = True

        self.raise_on_js_error = raise_on_js_error
