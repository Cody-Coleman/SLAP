# SLAP Automation Framework
=============
A python framework running selenium tests to drive integration, api, and end to end testing.
Test Automation projects get abandoned usually for one of 3 reasons:

1. It is to hard to write the tests to get good coverage.
2. It is to hard to maintain a test and update it as the project changes
3. It is to hard to run the tests quickly enough to be relevant.

When using this framework you need to keep in mind these issues, and design the tests and underlying verbs in a way to
make sure that the tests are easy to write / understand, easy to maintain, and easy to execute. SLAP accomplishes this
in the following ways:

1. Each test case is written in liner, and discrete, steps, in much the same way you'd write a manual test case.
There is no looping, logic, assignments or blocks in a test case, just the steps that are executed in a simple to
read manner. Each test case expects all actions to return true, and if not will fail the test at that step (It will not
continue running the steps after a failed point).

EXAMPLE:

```
def test_ti_login_0002(self):
    """
    Login: Failed login test, expected to fail
    @test Uses bad credentials to login, test is an example of a failure
    @author CodyC
    @date 04/29/18
    """
    # DEMONSTRATES NAVIGATING TO A LOGIN PAGE, WITH ERROR CODES FOR FAILURES AND CUSTOM ERRORS
    try:
        # NAVIGATE TO THE PAGE
        test(ti.go_to(location="The Internet", url=td.url), "GOTO_0000")
        # OPEN THE POPUP DIALOG
        test(ti.go_to(location="Form Authentication"), "GOTO_0001")
        # FILL OUT THE FORM
        test(ti.dialog(dialog='Login Page', user=td.bad_user, password=td.bad_pass), "DIALOG_0001")
        # VERIFY THE RESULTS OF THE LOGIN
        test(ti.verify(item="Authenticated"), "Failed to Authenticate")
    except Exception as e:
        ti.write(e, level='error')
        ti.take_screenshot(self.whoami())
        self.fail(e)
```





Installation Instructions:

    You must have a 3.6 version of python, to setup the automation to run locally (and executed against some remote environment)
    run the following command from the repositories root directory:
    
    sudo python setup.py
    
    This should install all the needed packages, download and setup webdrivers, and setup an example config file -> config.cfg
    
    Take a look at this file and make sure it's what you want / need for yoru configuration settings. 
    pycharm is by far the best IDE for any python code, and the community edition (free) will do everything you would need for this project

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
        ./slap.py -t ti_login_0001 -e dc12 -b chrome