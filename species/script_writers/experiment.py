
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
    OUTPUT_PATH_yaml_name = "OUTPUT_PATH"
    TOOL_PATH_yaml_name = "TOOL_PATH"
    ELASTIC_SEARCH_URL_yaml_name = "ELASTIC_SEARCH_URL"
    TITLE_yaml_name = "TITLE"

    def __init__(self, experiment_yaml):
        self.experiment = experiment_yaml
        self.timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if self.experiment["seed"]:
            random.seed(int(self.experiment["seed"]))

    def input_data_specification(self):
        ok, spec_file = get_string_or_environment_value(self.experiment['input_data_specification'])
        if not ok:
            error_out("'input_data_specification' is missing")
        if not os.path.isfile(spec_file):
            error_out(f"Specification file {spec_file} not found")
        return ok, spec_file

    def elasticsearch_url(self):
        ok, url = get_string_or_environment_value(self.experiment[self.ELASTIC_SEARCH_URL_yaml_name])
        return url

    def processed_folder(self):
        return f"{self.target_folder()}/{self.title()}/processed"

    def samples_folder(self):
        return f"{self.target_folder()}/samples"

    def target_folder(self):
        ok, output_path = get_string_or_environment_value(self.experiment[Experiment.OUTPUT_PATH_yaml_name])
        return output_path

    def get_output_folders(self):
        ok, output_path = get_string_or_environment_value(self.experiment[Experiment.OUTPUT_PATH_yaml_name])
        script_output_folder = None
        if ok:
            ok, script_output_folder = get_string_or_environment_value(f"{output_path}/{self.experiment[Experiment.TITLE_yaml_name]}")
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
        return self.experiment[Experiment.TITLE_yaml_name]

    def tool_folder(self):
        _, tf = get_string_or_environment_value(self.experiment[Experiment.TOOL_PATH_yaml_name])
        return tf

    def env_expand(self, s):
        if s is None:
            return None
        ok, tool_path = get_string_or_environment_value(self.experiment[Experiment.TOOL_PATH_yaml_name])
        if ok:
            ok, output_path = get_string_or_environment_value(self.experiment[Experiment.OUTPUT_PATH_yaml_name])
        if ok:
            ok, elastic_search_url = get_string_or_environment_value(
                self.experiment[Experiment.ELASTIC_SEARCH_URL_yaml_name])
        if ok:
            ok, title = get_string_or_environment_value(self.experiment[Experiment.TITLE_yaml_name])

        if ok:
            output_path = f"{output_path}/{self.title()}"
            return s.replace(Experiment.TOOL_PATH_yaml_name, tool_path)\
                .replace(Experiment.OUTPUT_PATH_yaml_name, output_path)\
                .replace(Experiment.ELASTIC_SEARCH_URL_yaml_name, elastic_search_url)\
                .replace(Experiment.TITLE_yaml_name, title)
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
        return self.script_line(Configuration.WAIT_UNTIL_STARTED)

    def sample_file_pattern(self):
        return self.experiment.env_expand(self.configuration["sample_file_pattern"])

    def configure(self):
        return self.experiment.env_expand(self.configuration["configure"])

    def is_started(self):
        return self.experiment.env_expand(self.configuration["is_started"])

    # segment specification
    def segment_size(self):
        return self.configuration["segment"]["size"]

    def minimum_number_words(self):
        return self.configuration["segment"]["minimum_number_words"]

    def script_line(self, s):
        if s in self.configuration:
            return self.experiment.env_expand(self.configuration[s])
        else:
            return f"# no {s} step specified"

    def post_process(self):
        return self.script_line("post_process")

    def prepare(self):
        return self.script_line("prepare")

    def summarize(self):
        return [ self.experiment.env_expand(line) for line in self.configuration["summarize"]]

    # sample configuration
    def sample_size_percent(self):
        sss = self.configuration["segment"]["sample"]["size"]
        if sss.endswith("%"):
            sss = sss[:-1]
        return sss

    def sample_size_info(self):
        return self.configuration["segment"]["sample"]["count"], self.sample_size_percent()