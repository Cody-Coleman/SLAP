#!/usr/bin/env python
import sys
import time
import os
import uuid
import urllib3
from library.helper import get_args, get_all_list, get_tc_list, set_env, run_tests, create_json_info

from shutil import rmtree, copy

from library.config import Config
from library.log import log_init

from urllib3.exceptions import InsecureRequestWarning

urllib3.disable_warnings(InsecureRequestWarning)

if __name__ == '__main__':
    # GET ARGS FROM ARG PARSER
    args = get_args()
    # Need to figure out where the config is, as automation may be executed from another path
    config_file_name = 'config.cfg'
    application_path = ''
    # If this is not executed from the actual directory it resides in:
    if not os.path.isfile(config_file_name) and not args.config:
        if hasattr(sys, 'frozen'):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.dirname(__file__)
        config_path = os.path.join(application_path, config_file_name)
    elif args.config:
        config_path = args.config
    else:
        config_path = config_file_name
    config = Config(config_path)

    config['run_id'] = uuid.uuid4().hex[:4]

    # GET LOG LEVEL FROM CONFIG
    lvl = config['log_level'] if config['log_level'] is not None else 1
    # OVERRIDE WITH COMMAND PROMPT
    if args.log_level >= 0:
        lvl = args.log_level

    # CHANGE THE DIRECTORY TO THAT INDICATED IN THE CONFIG FILE
    os.chdir(config['living_dir'])
    # CREATE A TIME STAMP FOR LOGGING
    tstruct = time.localtime()
    seconds = tstruct.tm_hour * 3600 + tstruct.tm_min * 60 + tstruct.tm_sec
    time_stamp = "{:02}_{:02}_{:02} {}".format(tstruct.tm_mon,
                                               tstruct.tm_mday,
                                               tstruct.tm_year,
                                               seconds)
    # CREATE DIRECTORY FOR OUTPUT LOGGING
    current_dir = os.path.join(config['output_dir'], 'current')
    if os.path.exists(current_dir):
        rmtree(current_dir, ignore_errors=True)
    os.makedirs(current_dir)

    # SET LOG, REPORT, and SS DIR
    config['log_dir'] = current_dir
    config['report_dir'] = current_dir
    config['screen_shot_dir'] = current_dir

    # CREATE THE HANDLERS
    log_init(lvl, config['log_dir'], config['run_id'])

    # FIGURE OUT WHAT KIND OF TEST WAS PASSED IN:
    test_list = []
    if args.test:
        test_list = args.test
    elif args.file:
        test_list = []
        # Get the basename of the file, which will be used for the xml name
        file_base = os.path.basename(args.file.name)
        # Populate the entries in the file into a list (array)
        for line in args.file:
            test_list.append(line.strip())
        args.file.close()
    elif args.suite:
        for module in args.suite:
            test_list += get_tc_list(module)
    elif args.all:
        for project in args.all:
            test_list += get_all_list(project)

    if args.list:
        # SORT THE LIST
        test_list = sorted(test_list, key=lambda z: (z, z[-4:]))
        print('\n' + '\n'.join(test_list))
        print("Total test_cases found: \n{}".format(len(test_list)))
        sys.exit(0)

    # NAME THE JSON FILE
    json_file = os.path.join(current_dir, "Test_Results_{}.json".format(config['run_id']))

    # SET XML FILE PATH AND TEST RUN
    config['json_file_path'] = json_file

    # POPULATE TESTRUN FOR XML OUTPUT
    config['browser'] = args.browser

    if args.device_type:
        config['device'] = args.device_type

    create_json_info()


    # SET THE ENVIRONMENT
    set_env(args, config)
    fail_count = 0
    for x in range(0, args.loop):
        fail_count = run_tests(test_list, time_stamp)

    output_dir = os.path.join(config['output_dir'], time_stamp)
    if args.save_log:
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)
        log_files = os.listdir(current_dir)
        for file_name in log_files:
            full_name = os.path.join(current_dir, file_name)
            if os.path.isfile(full_name):
                copy(full_name, output_dir)

    print("Total Failures: [{}]".format(fail_count))
    raise SystemExit(fail_count)
