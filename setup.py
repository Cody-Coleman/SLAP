from io import StringIO
from subprocess import call
from distutils import spawn
import platform
import argparse
import zipfile
import tarfile
import os

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set up a bunch of static strings
# set the approppropriate platform value for downloading from the appropriate place
platforms = {"Darwin": {"chromedriver": "mac64",
                        'geckodriver': 'macos',
                        "path_file": os.path.expanduser("~/.bash_profile")},
             "Linux": {"chromedriver": "linux32",
                       'geckodriver': 'macos',
                       "path_file": os.path.expanduser("~/.bash_profile")}}

config = {"chromedriver": {"version": "2.24",
                           "platform": platforms[platform.system()]["chromedriver"],
                           "location": "/usr/local/bin"},
          'geckodriver': {'version': "0.20.1",
                          'platform': platforms[platform.system()]['geckodriver'],
                          'location': '/usr/local/bin'}}

config["chromedriver"]["url"] = "http://chromedriver.storage.googleapis.com/{}/chromedriver_{}.zip" \
    .format(config["chromedriver"]["version"], config["chromedriver"]["platform"])

config['geckodriver']['url'] = "https://github.com/mozilla/geckodriver/releases/download/v{0}" \
                               "/geckodriver-v{0}-{1}.tar.gz".format(config['geckodriver']['version'],
                                                                     config['geckodriver']['platform'])


def dependencies():
    # Perhaps better if you use get_pip.py script via WGET or just use a decent version of python that includes
    # pip as part of the install
    if spawn.find_executable('pip') is None:
        call(["easy_install", "pip"])

    call(["pip", "install", "-r", "requirements.txt", "--upgrade", "--ignore-installed", "six"])
    call(["env", "ARCHFLAGS=-Wno-error=unused-command-line-argument-hard-error-in-future", "STATIC_DEPS=true",
          "pip", "install", "lxml"])


def chromedriver():
    # importing requests has to happen after pip installing requests
    import requests
    # CHROMEDRIVER
    print(f"\nGetting Chromedriver from '{config['cromedriver']['url']}'")
    r = requests.get(url=config["chromedriver"]["url"], verify=False)

    print(f"Extracting Chromedriver to '{config['chromedriver']['location']}'")

    c_zip = zipfile.ZipFile(mode="r", file=StringIO(r.content))

    try:
        c_zip.extractall(path=config["chromedriver"]["location"])
        os.chmod(os.path.join(config["chromedriver"]["location"], "chromedriver"), 0o777)
    except OSError as e:
        print("\nAre you root?")
        raise e


def geckodriver():
    import requests
    print(f"\nGetting Gecko Driver from '{config['geckodriver']['url']}'")
    r = requests.get(url=config['geckodriver']['url'], verify=False)
    print(f"Extracting to {config['geckodriver']['location']}")

    try:
        with open(config['geckodriver']['location']+"/geckodriver", 'wb') as f:
            f.write(r.content)
            os.chmod(os.path.join(config["geckodriver"]["location"], "geckodriver"), 0o777)
    except OSError as e:
        print("Are you Root?")
        raise e


def config_setup(ask_if_found=None):
    # CONFIG CREATION
    current_dir = os.path.abspath(__file__).split(__file__)[0][:-1]
    config_file = os.path.join(current_dir, "config.cfg")

    write_config = False
    if os.path.isfile(config_file) is True:
        if ask_if_found:
            overwrite_config = input(f"{config_file} already found\nWould you like to overwrite? [Y/N]: ")

            if overwrite_config.lower().replace(" ", "") in ("yes", "y"):
                print(f"Overwriting {config_file}")
                write_config = True

            else:
                print(f"Not overwriting {config_file}")

        else:
            print(f"\n{config_file} already found skipping config creation, run with --config to generate anyway")

    else:
        write_config = True

    if write_config is True:
        # NEEDS TO BE RECONFIGURED
        pass

def add_to_path():
    current_dir = os.path.abspath(__file__).split(__file__)[0][:-1]
    path_string = "PATH=$PATH:{}".format(current_dir)

    if spawn.find_executable('slap.py') is not None:
        print("\nslap.py apears to be in the PATH already")

    else:
        with open(platforms[platform.system()]["path_file"], "a") as bp:
            bp.write("\n")
            bp.write(path_string)

        print(f"\nAdded '{path_string}' to {platforms[platform.system()]}"
              f"\nIn the meantime, you'll need to 'source {platforms[platform.system()]}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Sets up SLAP so you can use it! no arguments installs everything")

    parser.add_argument('--deps', action="store_true",
                        help='Install the dependencies')

    parser.add_argument('--chromedriver', action="store_true",
                        help='install chromedriver')

    parser.add_argument('--geckodriver', action="store_true",
                        help='install geckodriver')

    parser.add_argument('--config', action="store_true",
                        help='writes out config.cfg and adds slap.py to the system PATH')

    args = parser.parse_args()

    if args.deps is True:
        dependencies()

    if args.chromedriver is True:
        chromedriver()

    if args.geckodriver is True:
        geckodriver()

    if args.config is True:
        config_setup(ask_if_found=True)
        add_to_path()

    if not any(vars(args).values()):
        dependencies()
        chromedriver()
        config_setup()
        add_to_path()

        print("Setup complete! You should now be able to run SLAP Tests")
