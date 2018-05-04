# BORG CONFIG OBJECT
# noinspection PyPackageRequirements
import yaml
import os


class Config(object):
    __shared_state = {}
    config = None

    def __init__(self, config_file=None):
        self.__dict__ = self.__shared_state
        self.config = self.load_config(config_file)

    def load_config(self, config_file=None):
        """
        Loads in the config from the config_path yaml file
        @param config_file: where to look for the file
        @return: self
        """
        if self.config is None and config_file is not None:
            print("Config has not been loaded, initializing config")
            with open(config_file, 'rb') as f:
                conf = yaml.load(f)
            conf = self.init_defaults(conf)
            return conf or u''
        else:
            return self.config

    def __getitem__(self, item):
        return self.config[item]

    def __setitem__(self, key, value):
        self.config[key] = value

    def __repr__(self):
        return yaml.dump(self.config)

    def __len__(self):
        return len(self.config)

    def __iter__(self):
        return iter(self.config)

    def __delitem__(self, key):
        del self.config[key]

    def __contains__(self, item):
        return self.config.__contains__(item)

    def keys(self):
        return self.config.keys()

    def items(self):
        return self.config.items()

    def values(self):
        return self.config.values()

    def update(self):
        self.config = yaml.load(open(self.config['CONFIG_PATH'], 'r'))

    def dump(self):
        yaml.dump(self.config, open(self.config['CONFIG_PATH'], 'w'), default_flow_style=False)

    def init_defaults(self, config):
        """
        Initializes the defaults if the values are None
        @return:
        """
        if config['living_dir'] is None:
            config['living_dir'] = os.getcwd()
        if config['test_data_dir'] is None:
            config['test_data_dir'] = os.path.join(config['living_dir'], 'Assets', 'TestData')
        if config['test_data_exclusion'] is None:
            config['test_data_exclusion'] = ''
        if config['error_code_dir'] is None:
            config['error_code_dir'] = os.path.join(config['living_dir'], "Assets", 'ErrorCodes')
        if config['js_snippet_dir'] is None:
            config['js_snippet_dir'] = os.path.join(config['living_dir'], 'Assets', 'JSSnippets')
        if config['error_code_exclusion'] is None:
            config['error_code_exclusion'] = ''
        if config['test_case_file'] is None:
            config['test_case_file'] = os.path.join(config['living_dir'], "test_cases.yaml")
        return config
