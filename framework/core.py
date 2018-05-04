## @package framework.core
# THIS FILE SHOULD NEVER REFERENCE A PRODUCT SPECIFIC ARENA
# The main verb holding pen for all other verb calls. if a verb is simple enough it will reside here. If there are a lot 
# of calls that are very close to the same for the verb, a sub verb should really be created and used, with a holding
# verb in this file put in place to find those
# sub verbs. Examples of subverbs are the go_to (handles all the navigation type requests), dialogs
# (fills out webforms) and products (configures the products for the company)
# The provisioning should get moved into it's own sub verb eventually as well
#

import functools
import inspect
import os
import re
import sys
import json
from time import time, localtime, sleep
from xml.etree import ElementTree as ET

import requests

from .driver import Driver
from library.config import Config

from library.test_data import map_yaml

import logging

logger = logging.getLogger(__name__)
config = Config()


class Core(object):
    """
        The Verbs class holds all other sub-verb calls. It is instantiated in the test_template.py file
        with a call making it a global variable of verbs = Verbs()
    """
    _shared_state = {}
    driver_state = False
    driver = None

    def __init__(self):
        """
            @return Verb Object
            @note sets self.driver to None 
        """
        self.__dict__ = self._shared_state

    def close_driver(self):
        """
          Closes the driver (browser) regardless of driver type, leaves that up to the Driver class. 
          @note Chrome driver prints an error message that the close failed and will now close.. harmless just annoying  
          @par EXAMPLE:
          verbs.close_driver()
        """
        if self.driver_state:
            self.driver.close_driver()
            self.driver_state = False
        return True

    def get_test_data(self, env=None):
        """
           Gets a TestData object and returns to the test case
           @param env (string) - If specified will set the ENV to this value in the config
           @return TestData Object
        """
        if env:
            logger.info('setting the ENV to {}'.format(env))
            config['environment'] = env
        logger.info("-" * 40)
        logger.info("Getting Test Data from yaml files")
        living_dir = config['living_dir'] if config['living_dir'] is not None else os.getcwd()
        test_data_path = config['test_data_dir'] if config[
                                                        'test_data_dir'] is not None else living_dir + "/Assets/TestData"
        test_data_exclusion = config['test_data_exclusion'].split(',') if config[
                                                                              'test_data_exclusion'] is not None else []
        logger.debug("TestData Path: {}".format(test_data_path))
        td = map_yaml(test_data_path, test_data_exclusion, config['environment'])
        return td

    @staticmethod
    def get_doc_string(doc_string):
        """
            Gets info about the test from the test_cases __doc__ string and sanitizes it
            @param doc_string (string) - The docstring from the function to add to the config TestRun 
            @return Dictionary - A dictionary of values from the doc string, using the XXXX: as the key and YYYYY as
                    the value
            @note This expects the docstring to follow the testCase docstring standard. see readme for info 
                  This only works on the test cases that haven't been moved to doxygen
            
        """
        # Need to Sanitize the doc string
        doc_dict = None
        try:
            doc_arg = (doc_string.strip()).split('\n')
            doc_dict = {}
            for val in doc_arg:
                try:
                    key, value = val.split(':')
                except ValueError:
                    key = ''
                    value = val
                key = key.strip()
                value = value.strip()
                doc_dict[key] = value
        except:
            logger.error("There was an error reading the test case doc string")
        return doc_dict

    def get_email(self, user=None, password=None, server=None, subject=None, message=None, wait=None, count=None,
                  return_raw_body=None):
        """
            Searches for an email containing a specific subject from a gmail based email server
            @param user (string) - The username to use for the email account
            @param password (string) - The password to use for the email account
            @param server (string) - The server to use for the email account
            @param subject (string) - The string to search for in the emails to find the reset url
            @param message (string) - The string to search for in the email body
            @param wait (int) - How long to wait for email, default's to 60
            @param count (int) - The number of emails we expect to find with this subject (optional)
            @param return_raw_body (bool) - If true, returns the raw email body payload as html_body and plain_body
            @return - string - Email body that matches subject filter
            @par EXAMPLE
            self.assertTrue(cp_core.email(user=td.email.user, password='Password', data=td.data))
        """
        html_body = None
        plain_body = None
        headers = None
        attachment = None
        # IMPORT NEEDED LIBRARY
        import imaplib
        import email
        from email.parser import Parser
        start_time = time()
        found = False
        sleep_time = 1
        wait = 75 if wait is None else wait
        while time() - start_time < wait:
            # LOGIN TO SERVER
            logger.info("Connecting to server {}".format(server))
            m = imaplib.IMAP4_SSL(server)
            logger.info("Attempting to login using user {} and password".format(user))
            m.login(user, password)
            # CHECK WHAT HAPPENS IF THIS FAILS
            # GET ALL EMAIL
            m.select("Inbox")
            logger.info("Searching for all emails with subject: {} and text: {}".format(subject, message))

            _, items = m.search(None, "({})".format(" ".join(filter(None,
                                                                    ['SUBJECT "{}"'.format(
                                                                        subject) if subject else None,
                                                                     'TEXT "{}"'.format(
                                                                         str(message)) if message else None]))))
            item_list = items[0].split()
            logger.info("Found {} emails".format(len(item_list)))
            if len(item_list) > 0:
                if count is None or count == len(item_list):
                    found = True
                    break
                elif len(item_list) > count:
                    logger.error("Expected %d emails. Already received %d." % (count, len(item_list)))
                    break
            sleep(sleep_time)
            sleep_time += 1

        if found:
            # USE THE LATEST EMAIL RECEIVED
            _, data = m.fetch(item_list[-1], "(RFC822)")
            complete_message = email.message_from_string(data[0][1])
            email_body = email.message_from_string(data[0][1]).get_payload()[0]

            for part in complete_message.walk():
                if part.is_multipart():
                    continue
                if part.get("Content-Disposition") is None:
                    continue
                attachment = part.get_filename()

            if return_raw_body:
                html_body = email_body.get_payload()
                plain_body = email_body.get_payload()
            else:
                html_body = email_body.get_payload()[1].get_payload()[0].get_payload()
                # Decode and delete line breaks from HTML body so we don't get them in the middle of URLs
                html_body = html_body.replace("=\r\n", "").replace("=3D", "=").replace("%3D", "=") \
                    .replace("&amp;", "&").replace("=20", " ").replace("&nbsp;", " ")
                html_body = re.sub(" *\r\n *", "", html_body)
                plain_body = email_body.get_payload()[0].get_payload()
            headers = Parser().parsestr(data[0][1])
        logger.info("Deleting emails")
        for num in item_list:
            m.store(num, '+X-GM-LABELS', '\\Trash')
        m.expunge()
        m.close()
        m.logout()

        return html_body, plain_body, headers, attachment

    def get_driver(self, browser_type=None, device_type=None):
        """
            Gets the driver type based on the value in the configs TestRun->browser section. This comes from 
            the command line, if nothing is passed will use firefox, otherwise uses whatever follows the -b switch
            @param browser_type (string) - Browser type
            @param device_type (string) - device type
            @note Currently supports Firefox, Chrome, and IE. is called from the TestTemplate class in test_template.py
            @par EXAMPLE:
            verbs.get_driver() 
        """
        if not browser_type:
            browser_type = config['browser']
        if not device_type:
            try:
                device_type = config['device_type']
            except:
                device_type = None

        # SANITIZE
        browser_type = browser_type.lower()
        browser_type = 'firefox' if browser_type is None else browser_type
        logger.info("Attempting to start the webdriver for %s" % browser_type)
        if self.driver_state:
            self.close_driver()

        self.driver = Driver(browser_type, device_type)
        self.driver_state = True

        if browser_type != 'ghost':
            x = config['window_x']
            y = config['window_y']
            self.driver.set_window_position(x if x else 0, y if y else 0)
            self.driver.set_window_size(1200, 1400)
        return self.driver

    @staticmethod
    def get_file_path(file_name=None, sanitize=None, start_directory=None):
        """
            Finds file of the given file name using os walk
            @param file_name (string) - The name of the file to find the path of
            @param sanitize (bool) - If set to False will not try to sanitize the file_name value
            @param start_directory (string) - If set will look in the Download folder instead of the Assets folder
            @par EXAMPLE
            from framework.core import Core
            Core.get_file_path("Survey 0001")
        """
        if sanitize is False:
            logger.debug("Skipping sanitation")
            plain_name = file_name
        else:
            plain_name = re.sub(" (\[(\w{2,4}_)?[a-zA-Z0-9]{10}\])", "", file_name)
            logger.info("Sanitized File Name: {}".format(plain_name))
        file_path = None
        import fnmatch
        if start_directory is None:
            start_directory = os.getcwd()
        for root, _, file_names in os.walk(start_directory):
            for filename in fnmatch.filter(file_names, plain_name):
                file_path = os.path.join(root, filename)
        if file_path is None:
            logger.debug("Couldn't find {}".format(plain_name))
        else:
            logger.debug("File path: %s" % file_path)
        return file_path

    @staticmethod
    def get_xml(file_name=None):
        """
            Gets the ElementTree of an XML document
            @param file_name (string)
        """
        file_path = Core.get_file_path(file_name)
        xml = ET.parse(file_path)
        return xml

    def indent(self, elem, level=0):
        """
            NAME: indent
            TITLE: indent an xml tree structure to make it easier to read
            PARM1: elem (ElementTree root) - the root to an ElementTree object
            PARM2: level (int) - how much to indent each level 
            RET: None, changes the element directly
            NOTES: This is only needed when printing an xml tree by calling tree.write() it makes it easier to read. 
        """
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            for e in elem:
                self.indent(e, level + 1)
                if not e.tail or not e.tail.strip():
                    e.tail = i + "  "
            if not e.tail or not e.tail.strip():
                e.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def log_result(self, result):
        """
            Logs the result, passed/failed to the config for later reporting
            @note This function is obsolete, instead simply use the write_result call
            @param result (string) - the result of the test be it passed or failed
            @note This sets the value in the config object that is later used for the xml report. 
            @par EXAMPLE:
            verbs.log_result('passed')
            @par 
            verbs.log_result('failed')
        """
        logger.info("-" * 40)
        logger.info("Verb: log_result")
        logger.debug("\n%s\n" % self.log_result.__doc__)
        config['result'] = result

    @staticmethod
    def make_unique(value):
        """
            Append a UUID to the string to avoid collisions
            @param value (string) - the string to make unique
        """
        import uuid
        return "{}_{}".format(value, uuid.uuid4().hex[0:10])

    def take_screenshot(self, filename=None):
        """
            Takes a screenshot of whatever state the browser is in
            @param filename (string) - If not set will use a default name ss.png
            @return None
            @par EXAMPLE:
            verbs.take_screenshot("c:\error.png")
        """
        file_dir = config['screen_shot_dir']
        logger.debug("Using {} as folder for screenshot path".format(file_dir))
        if not os.path.exists(file_dir):
            os.mkdir(file_dir)
        if filename is None:
            filename = 'ss'
        tstruct = localtime()
        seconds = tstruct.tm_hour * 3600 + tstruct.tm_min * 60 + tstruct.tm_sec
        ss_name = "PNG_{} {:02}_{:02}_{:02} {}.png".format(filename,
                                                           tstruct.tm_mon,
                                                           tstruct.tm_mday,
                                                           tstruct.tm_year,
                                                           seconds)
        full_path = os.path.join(file_dir, ss_name)
        logger.debug("Writing screenshot to {}".format(full_path))
        self.driver.save_screenshot(full_path)

    def timer(self, action):
        """
            starts or stops a timer
            @param action (string) - supports start and end only 
            @return None, sets the value in the config's TestRun->elapsed_time and start_time
            @note Used to determine the time the test took to run. a start is used in the startup
                    and a end in the teardown
            @par EXAMPLE:
            verbs.timer('start')
            @par 
            verbs.timer('end')
        """
        if action.lower() == 'start':
            config['start_time'] = str(time())
        elif action.lower() == 'end':
            start = float(config['start_time'])
            config['elapsed_time'] = str(int(time() - start))

    @staticmethod
    def sanitize(str_value):
        """
            Sanitize a string in order to make it easy to work with by removing leading or trailing
            whitespace, and replacing spaces inbetween the words with an underscore (_) as well
            @param str_value (string) - String to sanitize
            @return string
        """
        value = ((str_value.strip()).replace(' ', '_')).lower()
        value = value.replace('-', '_')
        logger.debug("sanitized [%s] to [%s]" % (str_value, value))
        return value

    @staticmethod
    def write(message, level='info'):
        """
            Writes output to logger object as info
            @param message (string) - message to write to the logger object
            @param level (string) - The level of message to log, supports info, debug, and error
            @return none
            @note This is just to keep consistency in test_cases in that they all call verb.something
            @par EXAMPLE:
            verbs.write("Deleting Customer")
            @par 
            verbs.write("Unable to connect", 'error')
            @par 
            verbs.write(message="Using secret hack", level="debug")
        """
        if level == 'info':
            logger.info(message)
        elif level == 'error':
            if sys.exc_info()[0] == AssertionError:
                # GET THE EXCEPTION DATA
                import traceback
                # EXCEPTION IS TUPLE WITH THREE PARTS
                _, exc_type, exc_tb = sys.exc_info()
                # GET THE FILENAME, LINE NUMBER, FUNCTION AND TEXT 
                # OF THE MOST RECENT EXCEPTION ON THE TRACEBACK STACK
                for frame in traceback.extract_tb(exc_tb, 1):
                    fname, lineno, fn, text = frame
                # COMPOSE STRING
                msg = "\n\n{:*<40}\n\n{: >20}: {}\n{: >20}: {}\n{: >20}: {}\n{: >20}: {}\n{: >20}: {}\n\n{:*<40}\n"
                message = msg.format('',
                                     type(exc_type).__name__, message,
                                     "FILE", fname,
                                     "FUNCTION", fn,
                                     "LINE NUMBER", lineno,
                                     "TEXT", text,
                                     '')
            logger.error(message)
        elif level == 'debug':
            logger.debug(message)

    def write_result(self, result):
        """
            Write the result of the test out to the xml output file
            @param result (Result) - Result object
            @return None
            @note Writes out the name, title, notes (from docstring) and results of the test as xml elements
            @par EXAMPLE:
            verbs.write_result()
        """
        test_result = dict()
        test_result['name'] = config['name']
        test_result['title'] = config['title']
        test_result['description'] = config['test']

        bug = config['bug']
        if len(bug) > 0:
            bug_url = config['bug_repo']
            if bug_url is None:
                bug_url = "http://localhost"
            test_result['bug'] = {'bug_text': bug, 'bug_link': os.path.join(bug_url, bug),
                                  'bug_status': get_bug_status(bug)}
        test_result['duration'] = config['elapsed_time']
        test_result['result'] = result
        output_file = config['json_file_path']
        logger.debug("Output File Path: {}".format(output_file))
        logger.debug("Checking if output file already exists")
        # if os.path.exists(output_file):
        #     logger.debug("Some results already collected, loading in results")
        with open(output_file, 'r') as outfile:
            other_results = json.load(outfile)
        other_results['test_cases'].append(test_result)
        with open(output_file, 'w') as outfile:
            outfile.write(json.dumps(other_results, sort_keys=True, indent=4))

def get_bug_status(bug_id):
    """
        Gets the status of the bug, and if verify or closed, the fix version as well
        @param bug_id (string) - The id of the bug in Jira to get
        @return (string) - The status and the fix version (if present) as a string
    """
    url = "https://companyname.atlassian.net/rest/api/2/issue/{}".format(bug_id)
    r = requests.get(url, auth=('apiuser', 'apipassword'), verify=False)
    result = None
    try:
        status = r.json()['fields']['status']['name']
        if status.lower() == 'verify' or status.lower() == 'closed':
            fix_version = r.json()['fields']['fixVersions'][-1]['name']
        else:
            fix_version = None
        result = "[{0}".format(status)
        if fix_version is not None:
            result += " - {0}]".format(fix_version)
        else:
            result += "]"
    except Exception as e:
        print(str(e))
    return result


class APIBadStatus(Exception):
    pass


class APIBadContent(Exception):
    pass


class APIBadFormat(Exception):
    pass


class BaseVerb(object):
    """
        Holds the logic for verb decoration.
    """

    def __init__(self, func):
        self.func = func

    def __call__(self):
        return BaseVerb.verb(self.func)

    def __get__(self, instance, instancetype):
        """Implement the descriptor protocol to make decorating instance method possible."""

        # Return a partial function with the first argument is the instance 
        #   of the class decorated.
        return functools.partial(self.__call__, instance)

    @staticmethod
    def verb(func):
        def wrap(*args, **kw):
            new_kw = {}
            data = None
            if 'data' in kw:
                data = kw['data']
            parms = inspect.getargspec(func)[0]
            # CREATE INITIAL PARAMETER LIST
            for p in parms:
                new_kw[p] = None
            # ASSIGN VALUES FROM DATA
            if data is not None:
                # ASSIGN ALL THE VALUES FROM DEFAULT TO THE PARAMETERS
                for key in data:
                    if key in new_kw:
                        new_kw[key] = data[key]
            # OVERWRITE WITH ANYTHING FROM KW
            for key in kw:
                new_kw[key] = kw[key]
            # OVERWRITE USING POSITIONAL ARGS
            if args is not None:
                for i in range(0, len(args)):
                    # CAN HAPPEN THAT POSITIONAL ARGUMENTS GET PASSED THAT WE DON"T CARE ABOUT
                    # NEED TO CATCH THE INDEXERROR THAT OCCURS AND JUST MOVE ON
                    try:
                        new_kw[parms[i]] = args[i]
                    except IndexError:
                        pass
            # GET THE FUNCTION NAME AND DO SOME PRINTING
            logger.info('-' * 40)
            str_list = func.__name__.split('_')
            str_list = map(lambda x: x[0].upper() + x[1:], str_list)
            str_list = ' '.join(str_list)
            logger.info("Verb: %s" % str_list)
            logger.debug("\n%s\n" % inspect.getdoc(func))

            logger.debug("Parameters given...")
            for kw in new_kw:
                if kw == 'driver':
                    continue
                # if type(new_kw[kw]) == unicode:
                #     logger.debug('Keyword {}: {}'.format(kw, new_kw[kw].encode('utf-8')))
                # else:
                #     logger.debug('Keyword {}: {}'.format(kw, new_kw[kw]))

            s = time()
            ret = func(**new_kw)
            logger.debug("verb dt: {} seconds".format(time() - s))
            return ret

        return wrap


# DECORATORS
def verb(func):
    """
        Verb decorator to handle the data default assignment as well as the print logging
        @param func (Function Object) - function to wrap
        @note - Only to be used on verbs that are called from test cases, not on internal functions
    """
    return BaseVerb.verb(func)
