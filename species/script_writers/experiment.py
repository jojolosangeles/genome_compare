
import datetime
import os
import random


def fs_ensure_folder_exists(path):
    """Create folder if it does not exist, return True if folder exists or was created, otherwise False"""
    if not os.path.exists(path):
        print(f"PATH {path} does not exist, CREATING IT")
        os.mkdir(path)
        if not os.path.exists(path):
            error_out(f"PATH {path} does NOT exist after creating it")
    if not os.path.isdir(path):
        print(f"PATH {path} is a FILE, and cannot be used as a folder")
        return False
    return True


def not_configured(s):
    return f"# {s} is NOT part of configuration"


def error_out(s):
    print(f"**** ERROR ****")
    print(s)
    exit(0)


def get_string_or_environment_value(s):
    """returns a tuple (success, value)
         success - boolean indicating value is valid
         value - a string value or None when 'success' is False
    """
    if s.startswith("env."):
        env_variable = s[4:]
        data = env_variable.split("/")
        env_value = os.environ.get(data[0])
        if env_value is None:
            print(f"WARNING: Environment variable {env_variable} must be set")
            return False, None
        else:
            if len(data) > 1:
                data[0] = env_value
                env_value = "/".join(data)
            return True, env_value

    return True, s


class Transformations:
    def __init__(self, transformations_yaml):
        self.transformations_yaml = transformations_yaml
        print(transformations_yaml)

    def min_word_length(self):
        return self.transformations_yaml["word_length_filter"]["min_length"]


class Experiment:
    OUTPUT_PATH_IN_YAML = "OUTPUT_PATH"
    TOOL_PATH_IN_YAML = "TOOL_PATH"
    ELASTIC_SEARCH_URL_IN_YAML = "ELASTIC_SEARCH_URL"
    TITLE_IN_YAML = "TITLE"

    def __init__(self, experiment_yaml):
        self.experiment = experiment_yaml
        self.timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if self.experiment["seed"]:
            random.seed(int(self.experiment["seed"]))

    def input_data_specification(self):
        ok, specfile = get_string_or_environment_value(self.experiment['input_data_specification'])
        if not ok:
            error_out("'input_data_specification' is missing")
        if not os.path.isfile(specfile):
            error_out(f"Specification file {specfile} not found")
        return ok, specfile

    def target_folder(self):
        ok, output_path = get_string_or_environment_value(self.experiment[Experiment.OUTPUT_PATH_IN_YAML])
        return output_path

    def get_output_folders(self):
        ok, output_path = get_string_or_environment_value(self.experiment[Experiment.OUTPUT_PATH_IN_YAML])
        script_output_folder = None
        if ok:
            ok, script_output_folder = get_string_or_environment_value(f"{output_path}/{self.experiment[Experiment.TITLE_IN_YAML]}")
        if ok:
            ok = fs_ensure_folder_exists(output_path)
        if ok:
            ok = fs_ensure_folder_exists(f"{output_path}/processed")
        if ok:
            ok = fs_ensure_folder_exists(f"{output_path}/samples")
        if ok:
            ok = fs_ensure_folder_exists(script_output_folder)
        return ok, output_path, script_output_folder

    def title(self):
        return self.experiment[Experiment.TITLE_IN_YAML]

    def env_expand(self, s):
        ok, tool_path = get_string_or_environment_value(self.experiment[Experiment.TOOL_PATH_IN_YAML])
        if ok:
            ok, output_path = get_string_or_environment_value(self.experiment[Experiment.OUTPUT_PATH_IN_YAML])
        if ok:
            ok, elastic_search_url = get_string_or_environment_value(
                self.experiment[Experiment.ELASTIC_SEARCH_URL_IN_YAML])
        if ok:
            ok, title = get_string_or_environment_value(self.experiment[Experiment.TITLE_IN_YAML])

        if ok:
            output_path = f"{output_path}/{self.title()}"
            return s.replace(Experiment.TOOL_PATH_IN_YAML, tool_path)\
                .replace(Experiment.OUTPUT_PATH_IN_YAML, output_path)\
                .replace(Experiment.ELASTIC_SEARCH_URL_IN_YAML, elastic_search_url)\
                .replace(Experiment.TITLE_IN_YAML, title)
        error_out("Expected environment variable NOT set, exiting")


class Configuration:
    WAIT_UNTIL_STARTED='wait_until_started'

    def __init__(self, experiment, configuration_yaml):
        self.experiment = experiment
        self.configuration = configuration_yaml

    # ES specific
    def install(self):
        return self.configuration["install"]

    def run(self):
        return self.experiment.env_expand(self.configuration["run"])

    def wait_until_started(self):
        if Configuration.WAIT_UNTIL_STARTED in self.configuration:
            return self.experiment.env_expand(self.configuration[Configuration.WAIT_UNTIL_STARTED])
        else:
            return not_configured(Configuration.WAIT_UNTIL_STARTED)

    def configure(self):
        return self.experiment.env_expand(self.configuration["configure"])

    def is_started(self):
        return self.experiment.env_expand(self.configuration["is_started"])

    # segment specification
    def segment_size(self):
        return self.configuration["segment"]["size"]

    # sample configuration
    def sample_size_percent(self):
        sss = self.configuration["segment"]["sample"]["size"]
        if sss.endswith("%"):
            sss = sss[:-1]
        return sss

    def sample_size_info(self):
        return self.configuration["segment"]["sample"]["count"], self.sample_size_percent()