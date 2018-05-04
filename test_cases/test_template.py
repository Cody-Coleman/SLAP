## @package test_cases.test_template
# Template used for test object that includes overloaded assertTrue/False to call the get_error_msg
#  that reads the error message out of the error message objects
# Also the init reads in the function string and adds it to the config object for reporting purposes
# Finally creates a core global object request_core for use in the test cases. 
import unittest
import inspect
import re
import yaml
from unittest.util import safe_repr
from xml.etree import ElementTree as et
from library.config import Config

core = None

import logging

logger = logging.getLogger(__name__)

class TestTemplate(unittest.TestCase):
    """
        Parent template to be used for all products test_cases
    """

    def __init__(self, name):
        """
            Test Template Initialization initializes a TestTemplate object with some pre-configured values
            @param name (string) - Name of the test to initialize
            @returns TestTemplate Object
            @note This setups up the verbs, assigns the config to it, calls the functions
            docstring and then initializes the action
        """
        config = Config()
        super(TestTemplate, self).__init__(name)
        self.doc_dict = None
        func = getattr(self, name)
        self.get_test_doc(name, func.__doc__)
        # ASSIGN VALUES TO CONFIG
        config['name'] = self.doc_dict['name']
        logger.info("NAME: {}".format(config['name']))
        config['title'] = self.doc_dict['title']
        logger.info("TITLE: {}".format(config['title']))
        config['test'] = self.doc_dict['test']
        logger.info("TEST: {}".format(config['test']))
        config['bug'] = self.doc_dict['bug']
        logger.info("BUG: {}".format(config['bug']))
          
    def get_test_doc(self, name, doc_string=None):
        """
            Writes out the test_cases doc string as well as assign it to key values in the config
            @param name (string) - The name of the test
            @param doc_string (string) - the doc string of the test to parse
        """
        # PARSE OUT THE DOXYGEN SETTINGS FROM THE STRING
        doc_string = doc_string if doc_string is not None else self._testMethodDoc
        doc_list = [x.strip().replace('\t', '') for x in doc_string.split('\n') if len(x.strip().replace('\t', '')) > 0]
        # CREATE DOC DICT OBJECT
        doc_dict = dict(name=name, title=doc_list[0], bug='', tags=[])
        for val in doc_list[1:]:
            if '@test' in val:
                doc_dict['test'] = val[5:]
            elif '@arg' in val:
                doc_dict['tags'] = [x.lower() for x in val[4:].split()]
            elif '@attention' in val:
                doc_dict['priority'] = val[10:]
            elif '@author' in val:
                doc_dict['author'] = val[7:]
            elif '@date' in val:
                doc_dict['date'] = val[5:]
            elif '@bug' in val:
                doc_dict['bug'] = val[4:].strip()
            elif '@version' in val:
                doc_dict['version'] = int(val[8:].replace(".", ""))
            elif '@deprecated' in val:
                doc_dict['deprecated'] = True
            elif '@note' in val:
                env_result = re.findall('ENV=(\w+)', val.upper())
                if len(env_result) > 0:
                    doc_dict['datacenters'] = env_result
                env_not = re.findall('ENV!=(\w+)', val.upper())
                if len(env_not) > 0:
                    doc_dict['no_environment'] = env_not
                priority = re.findall('priority=(\d)', val.lower())
                if len(priority) > 0:
                    doc_dict['priority'] = priority[0]
                else:
                    doc_dict['note'] = val[5:]
        # CHECK IF TITLE AND NOTE NOT IN DOC_DICT
        if 'title' not in doc_dict:
            doc_dict['Title'] = 'TEST DOCUMENTATION DOES NOT INCLUDE THE TEST TITLE'
        if 'test' not in doc_dict:
            doc_dict['Test'] = 'TEST DOCUMENTATION DOES NOT INCLUDE TEST DESCRIPTION'
        self.doc_dict = doc_dict

    def assertFalse(self, expr, msg=None, data=None):
        """Check that the expression is false."""
        if expr:
            # GET ERROR MESSAGE FROM XML
            msg = self.get_error_msg(msg)
            # CHECK FOR DATA
            if data is not None:
                import pprint
                msg += " WITH DATA %s" % pprint.pprint(data)
            # COMPOSE MESSAGE AND RAISE
            msg = self._formatMessage(msg, "%s is not false" % safe_repr
                                      (expr))
            raise self.failureException(msg)

    def assertTrue(self, expr, msg=None, data=None):
        """Check that the expression is true."""
        if not expr:
            # GET ERROR MESSAGE FROM YAML
            msg = self.get_error_msg(msg)
            # CHECK FOR DATA
            if data is not None:
                import pprint
                msg += " WITH DATA {}".format(data)
            # COMPOSE MESSAGE AND RAISE
            msg = self._formatMessage(msg, f"{safe_repr(expr)} is not true")
            raise self.failureException(msg)

    def get_error_msg(self, msg='E9999'):
        """
            gets error message
        """
        config = Config()
        # READ XML FILE AND PARSE TO XML OBJECT
        error_dir = config['error_code_dir']
        exclusion = config['error_code_exclusion']
        file_list = []
        import os
        for filename in os.listdir(error_dir):
            if filename.endswith('yaml') and filename not in exclusion:
                file_list.append(os.path.join(error_dir, filename))
        # Read in all the files and assign them to an ET Root
        error_config = {}
        for filename in file_list:
            config = yaml.load(open(os.path.join(error_dir, filename), 'rb'))
            error_config.update(config['errors'])

        # FIND THE ERROR CODE BY BREAKING DOWN THE msg
        if len(msg.split()) == 1:
            # THIS COULD BE A SPECIAL ERROR MESSAGE
            for key in error_config.keys():
                if key in msg.lower():
                    error_val = int(msg.split('_')[1])
                    return error_config[key][error_val]
        return msg

    def ok_to_run(self):
        """
            Checks the docstring of the test and if either the version doesn't match or the env, will skip the test
        """
        # READING DOC STRING, LOOKING FOR VERSION
        doc_dict = self.doc_dict
        skip_test = False
        msg = ''
        if 'deprecated' in doc_dict:
            msg = "This test has been deprecated"
            skip_test = True
        elif 'version' in doc_dict and int(self.core.config.get('TestRun', 'driver_version')) < doc_dict['version']:
            msg = "Features unavailable in this version: {}".format(doc_dict['version'])
            skip_test = True
        elif 'datacenters' in doc_dict and len([s for s in doc_dict['datacenters'] if s in self.core.config.get('TestRun', 'datacenters')]) == 0:
            msg = "Test only works in {}".format(doc_dict['datacenters'])
            skip_test = True
        elif 'no_environment' in doc_dict and self.core.config.get('TestRun', 'datacenters').upper() in doc_dict['no_environment']:
            msg = "Test does not work in {}".format(doc_dict['no_environment'])
            skip_test = True
        if skip_test:
            self.core.write("\n" + "_" * 40 + "\n{}".format(msg), level='error')
            if self.core.driver is not None:
                self.core.driver.close_driver()
                self.core.driver_state = False
            self.skipTest(msg)

    def whoami(self):
        """
            returns the method name
        """
        func_name = inspect.stack()[1][3]
        if func_name[:5] == 'test_':
            return func_name[5:]

