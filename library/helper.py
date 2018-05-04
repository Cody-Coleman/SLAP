import argparse
import inspect
import os
import platform
import re
import socket
import unittest
import json
import yaml
import importlib
from library.log import log_to_file


import logging

from library.config import Config

logger = logging.getLogger(__name__)


def find_tc(test_name):
    """
        Finds the test case test from the test case object by name
        @param: test_name(string) - the name of the test case, such as 'test_0001'
        @param: config(Configuration Object) The config object to pass to the test case once found
        @return: Unit Test test case object
        @note: will find the test case based on the name regardless of where in the test_cases package it's located
    """
    config = Config()
    with open(config['test_case_file'], 'rb') as f:
        tc_config = yaml.load(f)

    for k, v in tc_config.items():
        for package in v:
            module = importlib.import_module(f'test_cases.{k}.{package}')
            for _, oj in inspect.getmembers(module):
                if inspect.isclass(oj):
                    if hasattr(oj, test_name):
                        return oj(test_name)
    return None


def find_staging(config):
    """
        Finds what ENV to use for the staging value in the config by searching IN the env for the matching option
    @param config:
    @return:
    """
    for item in config.options('Staging'):
        if item.upper() in config.get_config_value('ENVIRONMENT'):
            return config.get('Staging', item.upper())


def get_args():
    """
        Pulls the arguments off the commandline and parses using rules
        @return parser object
        @note all commandline options and tweaks must be done to this function.
    """
    parser = argparse.ArgumentParser(description="Executes one or more integration test using"
                                                 " a mix of Selenium and REST api calls")
    # Create a group to add options that are exclusive for each other
    # namely you can do -t or -f but not both
    group = parser.add_mutually_exclusive_group(required=True)
    parser.add_argument('-b', '--browser', default='firefox',
                        help='Select which browser to use for the test: [chrome, ie, firefox, custom_mobile]')
    parser.add_argument('-d', '--device_type',
                        help='Select which device to use for the test: [iPhone, iPad, Android]')
    parser.add_argument('-c', '--config',
                        help='Path to the config.cfg file')
    parser.add_argument('--dev_only', action='store_true',
                        help='When set, will use only dev_xxx.tdx files and ignore prod_xxx.tdx files, '
                             '')
    parser.add_argument('-e', '--env',
                        help='Test Environment to use (DC1, DC2, DEV1, DEV2, etc)')
    parser.add_argument('-i', '--testrun', type=int, default=0,
                        help='TestRun Id value, defaults to 0 if not included')
    parser.add_argument('-l', '--log_level', type=int, default=-1,
                        help='Log level to print to console, 0 is debug, 1 is default '
                             '(info and error), 2 is just results')
    parser.add_argument('--loop', default=1, type=int,
                        help='Will loop [x] amount of times over the list of test_cases passed in')
    parser.add_argument('--save_log', action='store_true',
                        help='enable logging the output to file (timestamp.log)')
    parser.add_argument('--agent', help="When specified will execute test_cases as if this agent")
    parser.add_argument('--list', action='store_true',
                        help="When set will instead list all test_cases found. Only useful with -f, -s, or -a")
    # GROUP ARGUMENTS

    group.add_argument('-a', '--all', nargs='+',
                       help='Run all the test_cases, you can pass in a project name initial to specify only those test_cases')
    group.add_argument('-f', '--file', type=argparse.FileType('r'),
                       help='A file containing a list of test_cases')
    group.add_argument('-s', '--suite', nargs='+',
                       help='Suite of test_cases in the Module name to run')
    group.add_argument('-t', '--test', nargs='+',
                       help='The test to run')

    try:
        return parser.parse_args()
    except:
        # parser.print_help()
        exit()


def get_os_info():
    """
        finds OS info such as the os, dist, ip, and bit type that the automation is running on
        @return tuple (os, ip, dist, bit) 
        @note is cross platform compatible, should work fine on windows, linux
        @note Not sure what the return of platform.system() is for mac so didn't include it
    """
    os = platform.system()
    try:
        ip = socket.gethostbyname(socket.gethostname())
    except socket.gaierror:
        ip = "127.0.0.1"
    dist = ''
    if os == 'Windows':
        release, version, csd, _ = platform.win32_ver()
        dist = "{} {} {}".format(os, release, csd)
    elif os == 'Linux':
        release, version, csd = platform.dist()
        dist = "{} {} {} {}".format(os, release, version, csd)
    elif os == 'Darwin':
        release, version, _ = platform.mac_ver()
        os = 'Mac OS'
    bit = platform.machine()
    hostname = socket.gethostname()
    return os, ip, dist, bit, hostname


def get_tc_list(module_name):
    """
        Returns a list of test cases names (strings) to be executed by calling find_tc
        @param module_name (string) - The module (dot py file)  to pull all the test_cases from
        @return tc_list (string List)
    """
    # LOADING THE TC CONFIG
    config = Config()
    tc_list = list()
    # REGEX TO FIND TEST CASES IN THE TEST CLASS
    comp = re.compile("(test_)([a-z_0-9]+?)(\d{4}$)")
    tmp_list = module_name.split('_')
    # CONVERT THE MODULE NAME TO CLASS NAME, MUST FOLLOW THIS FORMAT
    class_name = tmp_list[0].upper() + tmp_list[1][0].upper() + tmp_list[1][1:]
    # LOAD THE TEST CASE YAML
    with open(config['test_case_file'], 'rb') as f:
        test_case_config = yaml.load(f)

    # FIND THE PARENT MODULE THAT HAS THE TEST SUITE MODULE
    for m_name in test_case_config:
        if module_name in test_case_config[m_name]:
            # THIS IS THE RIGHT MODULE THAT WE ARE LOOKING FOR SO IMPORT THE SUB MODULE
            idx = test_case_config[m_name].index(module_name)
            module = importlib.import_module(f"test_cases.{m_name}.{test_case_config[m_name][idx]}")
            test_class = getattr(module, class_name)
            for name in test_class.__dict__:
                if comp.match(name):
                    tc_list.append(name)
            #tc_list.append(tmp_data)
    return tc_list


def get_all_list(project=None):
    """
        Returns a list of all test cases found in the project 
        @param project (string) - If set will only return the test cases for that project (ts, rep, rs, ta) 
        @return (list of strings) - Returns a list of Testcase names found by parsing through the modules
    """
    # GET A COPY OF GLOBALS TO WORK WITH
    g = globals().copy()
    tc_list = []
    comp1 = re.compile("(test)(?P<project>_\w+?_)([a-z_]+?)(\d{4}$)")
    comp2 = re.compile("(test)(_%s_)([a-z_]+?)(\d{4}$)" % project)
    # IF project == all SET TO NONE
    project = None if project == 'all' else 'test_%s_' % project
    for val in g:
        for _, obj in inspect.getmembers(g[val]):
            if inspect.isclass(obj):
                for key in obj.__dict__:
                    # USE SOME REGEX TO SEE IF THIS IS THE RIGHT MODULE NAME
                    if project and comp2.match(key):
                        tc_list.append(key)
                    elif not project and comp1.match(key):
                        tc_list.append(key)
    return tc_list


def get_test_metadata(test_list):
    """

    :param test_list:
    :return:
    """
    config = Config()
    metadata_list = list()
    # GET THE TEST ID
    for test_name in test_list:
        # APPEND test_ IF NOT PRESENT
        test_name = test_name.replace("test_", "")
        full_test_name = 'test_' + test_name if test_name[:5] != 'test_' else test_name

        test_object = find_tc(full_test_name)
        assert test_object, "Failed to find any test case named '{}'".format(test_name)
        test_id_list = re.findall("test_([a-zA-Z_]+?\d{4})", full_test_name)
        assert len(test_id_list) == 1, "Test name does not follow pattern"
        # GET THE DOC STRING INTO A DICTIONARY
        doc_dict = test_object.doc_dict
        test_cases = {"": ""}
        try:
            if 'note' in doc_dict and type(eval(doc_dict['note'])) is dict:
                test_cases = eval(doc_dict['note'])
        except Exception:
            print("Note is not a dictionary")

        # MAKE A TESTCASE FOR EACH TEST IF A DICTIONARY IS ADDED
        for key, val in test_cases.iteritems():
            test_metadata = test_object.doc_dict.copy()
            test_metadata['name'] = "{}{}".format(test_metadata['title'], " %s" % key if key else "")
            test_metadata['script_id'] = "{}{}".format(test_name, " %s" % val if val else "")
            comp = re.compile("# (.+)\n")
            test_metadata['steps'] = [x.capitalize().replace('"', '') for x in
                                      (comp.findall(inspect.getsource(getattr(test_object, full_test_name))))]
            if 'priority' not in test_metadata:
                test_metadata['priority'] = 3
            if 'result' not in test_metadata:
                test_metadata['result'] = test_metadata['test'].replace('"', '')
            metadata_list.append(test_metadata)
    return metadata_list


def run_tests(test_list, time_stamp):
    """
        Runs all the test_cases in the list and updates all values
        @param test_list: List of test_cases to run
        @param time_stamp: I'm sure it's used for something
        @return:
    """

    config = Config()
    # PARAMETERS
    fail_count = 0
    fail_array = ""
    fail_padding_left = ""
    fail_padding_right = ""
    count = 0
    comp = re.compile('(?:\w+?)_(\w+?)_(?:.+)')

    # TEST LOOP
    for test in test_list:
        # CREATE LOGFILE
        # NEED TO WRITE A NEW LOG FILE PER TEST, THE LOGGER DOESN'T SUPPORT THIS
        config['log_file'] = "LOG_{} {}.log".format(test, time_stamp)
        full_path = os.path.join(config['log_dir'], config['log_file'])
        log_to_file(full_path, logger, config['run_id'])
        logger.debug("Hostname: {}".format(config['hostname']))
        count += 1
        if type(test) != dict:
            if not test.startswith('test_'):
                test = 'test_{}'.format(test)
        config['testname'] = test
        # GET TEST PROJECT
        project_name = comp.findall(test)
        if len(project_name) == 1:
            logger.debug("Project Name: {}".format(project_name[0]))
            # SET UNIQUE VALUE IN CONFIG
            config['run_id'] = "{}_{}".format(project_name[0], config['run_id'])
        else:
            logger.debug("Project Name not found: {}".format(test))
        # Create the test case object after finding it in the test_cases package
        tc = find_tc(test)
        # get_test_metadata(tc, test)
        if tc is not None:
            # WRITE OUT PERTINENT DATA FOR NOTIFICATION
            test_result = unittest.TextTestRunner().run(tc)
            logger.debug("\nTestResult: {}".format(test_result))
            if (len(test_result.failures) > 0) or (len(test_result.errors) > 0):
                fail_count += 1
                status = 'Failed'
                if fail_array == "":
                    fail_array = test
                else:
                    fail_array += " " + test
            else:
                status = 'Passed'
            logger.info("TEST {1}/{2}: {0}: {3}".format(test, count, len(test_list), status))
            if fail_array != "":
                fail_padding_left = " ("
                fail_padding_right = ")"
            logger.info("TOTAL FAILURES: {}{}{}{}".format(fail_count,
                                                          fail_padding_left,
                                                          fail_array,
                                                          fail_padding_right))
        else:
            logger.error('Test case [{}] was not found'.format(test))
            fail_count += 1
            # logger.disable_log()
    return fail_count


def set_env(args, config):
    """
        Sets the datacenters for the test automation to run in, checking for an agent flag or config value. If found
        will prepend the agent name to the env, otherwise just uses the datacenters and sets it in the config object
        @param args (Argument Object) - Holds all the arguments
        @param config (Config Object) - Holds the config
    """
    environment = config['environment']
    logger.debug("Config ENV: {}".format(environment))
    logger.debug("Arg ENV: {}".format(args.env))
    # SET THE ENV ACCORDING TO THE COMMAND LINE
    if args.env:
        environment = args.env

    # BEFORE GETTING ENV NEED TO CHECK FOR AGENT VALUE
    agent = config['agent'] if 'agent' in config else None
    if args.agent is not None:
        agent = args.agent
    if agent is not None:
        environment = "{}{}".format(agent, environment)

    logger.info("Setting final env in config as: {}".format(environment.lower()))
    config['environment'] = environment.lower()


def file_path(file_name=None, sanitize=None, start_directory=None):
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
        logger.debug("File path: {}".format(file_path))
    return file_path


def create_json_info():
    """

    @return:
    """
    config = Config()
    # Get the OS, dist (7, 2012, minty, ubuntu), and bit (32 or 64) of the running system
    (opsys, ip_addr, dist, bit, hostname) = get_os_info()
    # Assign the values to the TestRun so that they are available in the xml report
    config['os'] = opsys
    config['ip'] = ip_addr
    config['dist'] = dist
    config['bit'] = bit
    config['hostname'] = hostname
    print("Hostname is {}".format(hostname))

    output_file = config['json_file_path']
    test_run_dict = dict()
    test_run_dict['name'] = config['hostname']
    test_run_dict['run_id'] = config['run_id']
    test_run_dict['os'] = config['os']
    test_run_dict['ip'] = config['ip']
    test_run_dict['browser'] = config['browser']
    test_run_dict['dist'] = config['dist']
    test_run_dict['ip'] = config['ip']
    test_run_dict['test_cases'] = []

    if not os.path.exists(config['output_dir']):
        os.mkdir(config['output_dir'])
    with open(output_file, 'w') as outfile:
        outfile.write(json.dumps(test_run_dict, sort_keys=True, indent=4))
