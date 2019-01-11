# SLAP Automation Framework

A python framework running selenium tests to drive integration, api, and end to end testing.
This framework is designed behind these 3 principles, principles that when not followed usually lead to automation abandonment


## The Three Principles
1. It must be easy to write the tests to get good coverage.
2. It must be easy to maintain the tests and update them as the project changes
3. It must be easy to run the tests quickly enough, and specifically enough, to be relevant.

--------
When using this framework you need to keep in mind these issues, and design the tests and underlying verbs in a way to
make sure that the tests are easy to write / understand, easy to maintain, and easy to execute. SLAP accomplishes this
in the following ways:

1. Each test case is written in liner, and discrete, steps, in much the same way you'd write a manual test case.
There is no looping, logic, assignments or blocks in a test case, just the steps that are executed in a simple to
read manner. Each test case expects all actions to return true, and if not will fail the test at that step (It will not
continue running the steps after a failed point).

EXAMPLE:

```python
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

The `#` in the example for the comments indicate a test step, and make it possible to extract test steps out of an automated test and into
a test case management solution of some sort.


Notice that the test case has no logic in it, just simple steps testing a single discrete action. All the logic in the test case is hidden in the _verbs_ **go_to**
**dialog** and **verify**

This simple test case also meets the second requirement as it is easy to maintain. It is easy to see from this view what the test steps are, what data they are passing in, and what
calls they are making. If any of these need to be changed, or extra steps added or removed as time goes on, it's clear to see at what point in the test these changes need
to be made.


2. Every _verb_ returns either True or False, and the test expects True if it was successful. This is done by wrapping the verb in such a way that if all
calls are successful the _verb_ returns **True** and if there are any exceptions the _verb_ returns **False**. This simple logic means that you do not
need to handle all the possible exceptions in every single verb, just write the actions in the verb with the expectation that the calls will be successful and
know that if there are any errors, the test will fail on that step



## Setup
The SLAP framework takes two configuration files. A main configuration file called **config.yaml**, and a test case configuration file called **test_cases.yaml**
The configuration file name can be change on the command line by passing in a -c when running the **slap.py** main entry point. The config expects to have
all the values listed in the config_exmaple.yaml, so just copy that and rename to config.yaml. Look through all the settings and make sure they are what you need them to be, as far as
what gets included and excluded into the framework.

The **test_cases.yaml** lists out all the projects and test cases that the framework is aware of and will try to load and find. **SLAP** does not just run all the tests,
you must tell it which individual test, suite or file of tests to run and it will find these libraries and start execution. (Do not get this integrated and e2e framework c
confused with a unittest framework, the execution and use case is very different)

As an example:
```yaml
---
the_internet:
- ti_login
- ti_forms
the_other_internet:
- toi_login
- toi_forms
```

Where _the_internet_ and _the_other_internet_ are package names of folders located under the _test_cases_ package folder, and the list of packages _ti_login_ and _ti_forms_ are a suite of tests containing
the test classes and test cases.

This way as more tests are developed and more projects added to the framework, you only need to update this yaml file of what modules and packages (and therefore classes and test cases) to load.


## Running Tests
In order to ensure the **3.** principle, SLAP does not just blindly run all the tests it finds. Instead you must specify what test or tests you want executed on the command line.
This is done to ensure the framework lends itself well to things like:
1. Parallel execution, multiple agents with the framework pull from a queue of tests and execute as tests are delivered to them
2. Build Tools that run subset of tests can either do so through a file that gets updated, or passing a long list of tests
3. Quickly run targted tests against a specific area, this is done by allowing one to run all tests in a suite
4. Run just the failed tests. If you run a large suite of tests and gather all the failures, you are able to easily re-execute the failed tests

You can pass a list of tests with the _-t_ flag, a suite of tests using the _-s_ flag or a file that contains line seperated test ids using the _-f_ flag

### Test Cases by Name

To execute a test case by name you'd do something like the following:
```
slap.py -t ti_login_0001
```
To execute more than one test, you provide a space seperated list:

```
slap.py -t ti_login_0001 ti_login_0002
```

### Test Cases by Suite

Sometimes it's helpful to execute all the tests in a suite (say the login module broke, was fixed and you want to run just the login tests)

To accomplish this you'd pass in the **package name** as listed in both the test_cases.yaml and as the actual file. So assuming that we have a
tree structure of
```
SLAP
 - test_cases
   - __init__.py
   - the_internet
     __init__.py
     - ti_login.py
     - ti_forms.py
```

To run all the login tests the following command would be used:
```
slap.py -s ti_login
```

The framework will then find all the test cases in that project, create a test list and then execute them. This ends up executing like:
```
slap.py -t ti_login_0001 ti_login_0002 ti_login_0003 ti_login_0004
```


You can also pass in multiple suites the same as you can pass in multiple tests, by just separating test suites by spaces:
```
slap.py -s ti_login toi_forms
```

And the suites do not have to belong to the same project.

### Test Cases by File
When passing in a file, SLAP will parse it and create a test case list out of each line of the file as an example, if there was a file called _smoke_tests_ that had
the following contents:
```
ti_login_0001
ti_login_0003
```
you would execute this file like so:
```
slap.py -f smoke_tests
```


## Reading The Results

By default the SLAP framework outputs the **LOG**, **ERROR** and **CRITICAL** level logs to standard out. It also creates a file named after the test case
and time stamped that includes the **DEBUG** level logs. This way you don't need to enable debug level logs to view the results of a test case or test run on screen

When there is a failure, the log file will write out the line and test case in such a way to make it easy to spot in the logs:
```
05-04 09:44:19 - [ti_e17c: ERROR] - [framework.the_internet.ti_core:133] - Timed Out waiting for page to load or element to be found:

Message: Value: //h2[contains(text(), 'Secure Area')], by: xpath, wait: 10

05-04 09:44:19 - [ti_e17c: ERROR] - [framework.core:414] -

****************************************

      AssertionError: Failed to Authenticate
                FILE: /Users/CodyC/Documents/workspace/SLAP/test_cases/the_internet/ti_login.py
            FUNCTION: test_ti_login_0002
         LINE NUMBER: 100
                TEXT: test(ti.verify(item="Authenticated"), "Failed to Authenticate")

****************************************
```

Here we can see that the _verb_ located at **framework.the_internet.ti_core:133** failed with an error waiting for an element to show up
It then logs what step in the test case and test name that this failure occurred on.

Whenever a test fails, if you include
```
 {core}.take_screenshot(self.whoami())
```
in the finally statement, a screenshot of what was on the screen at failure will be recorded.

All files get dropped into whatever directory that is specified in the _config.yaml_ as the output directory. It is almost always a good idea to have this
directory different than where the framework code lives.

Also, at the end of the run, SLAP will create a summary .json file. An example of which would look like:
```json
{
    "browser": "firefox",
    "dist": "",
    "ip": "127.0.0.1",
    "name": "Q-C02MX08HFH04-CodyC",
    "os": "Mac OS",
    "run_id": "e17c",
    "test_cases": [
        {
            "description": " Attempt login using a webform and submitting username and pass",
            "duration": "5",
            "name": "test_ti_login_0001",
            "result": "passed",
            "title": "Login: Login using form"
        },
        {
            "description": " Uses bad credentials to login, test is an example of a failure",
            "duration": "15",
            "name": "test_ti_login_0002",
            "result": "failed",
            "title": "Login: Failed login test, expected to fail"
        }
    ]
}
```

This is so that other tools can be used to upload the results of tests to build tools, or test case management solutions.

On each new run, the contents of the output directory / current are scrubbed. If you'd like to retain logs so that you can review them later, include the ```--save_log```
flag on the command. This will cause SLAP to timestamp the current folder to preserve the logs

