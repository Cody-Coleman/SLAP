PUP README
	Instructions and a helpful guideline to getting started with creating automation

Installation Instructions:

    You must have a 2.7 version of python, to setup the automation to run locally (and executed against some remote environment)
    run the following command from the repositories root directory:
    
    sudo python setup.py
    
    This should install all the needed packages, download and setup webdrivers, and setup an example config file -> config.cfg
    
    Take a look at this file and make sure it's what you want / need for yoru configuration settings. 
    pycharm is by far the best IDE for any python code, and the community edition (free) will do everything you would need for this project
    
	
Git Repository
	ssh://git@gitlab-app.eng.qops.net:10022/testing/PUP.git

Commenting Guidelines

	Verb/Function Commenting
		"""
            Here is where a short description goes
            @param name (type) - description
            @author name
            @date 1/1/2001
            @par EXAMPLE
            self.assertTrue(here.is(action="an example", of_how_to="call the verb"), "ERROR message")
		"""

	Test Case Commenting
		"""
            Example: It tests this
            @test Here is a description of what it does
            @author name
            @date 1/1/2001
        """

Command Line Parameters:

    -h, --help            show this help message and exit
    -b BROWSER, --browser BROWSER
                        Select which browser to use for the test: [chrome, ie,
                        firefox]
    -c CONFIG, --config CONFIG
                        Path to the config.cfg file
    --dev_only            When set, will use only dev_xxx.tdx files and ignore
                        prod_xxx.tdx files,
    -e ENV, --env ENV     Test Environment to use (ST1, CO1, etc)
    -i TESTRUN, --testrun TESTRUN
                        TestRun Id value, defaults to 0 if not included
    -j JFE, --jfe JFE     JFE State for FEAST tests(NULL,0,1,FORCE,HARD)
    -l LOG_LEVEL, --log_level LOG_LEVEL
                        Log level to print to console, 0 is debug, 1 is
                        default (info and error), 2 is just results
    --loop LOOP           Will loop [x] amount of times over the list of tests
                        passed in
    --save_log            enable logging the output to file (timestamp.log)
    -v, --verbose         write out the actions taken by the script
    -z [ZEPHYR], --zephyr [ZEPHYR]
                        Checks the Zephyr for the test, and either updates it,
                        or adds a new test takes the project name (ts, rs,
                        rep, dis, ta)
    --agent AGENT         When specified will execute tests as if this agent
    --list                When set will instead list all tests found. Only
                        useful with -f, s, or a
    -a ALL [ALL ...], --all ALL [ALL ...]
                        Run all the tests, you can pass in a project name
                        initial to specify only those tests
    -f FILE, --file FILE  A file containing a list of tests
    -s SUITE [SUITE ...], --suite SUITE [SUITE ...]
                        Suite of tests in the Module name to run
    -t TEST [TEST ...], --test TEST [TEST ...]
                        The test to run

Examples

    Running a test:
        ./pup.py -t rs_d_messages_0001 -e az1 -r chrome

    Adding a test to Zephyr:
        ./pup.py -t new_test_0001 -z ProjectNameInZephyr