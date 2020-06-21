
import os
import datetime


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
        env_value = os.environ.get(env_variable)
        if env_value is None:
            print(f"WARNING: Environment variable {env_variable} must be set")
            return False, None
        else:
            return True, env_value

    return True, s


class Experiment:
    def __init__(self, experiment_yaml):
        self.experiment = experiment_yaml
        self.timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def get_output_folders(self):
        ok, output_path = get_string_or_environment_value(self.experiment["output_path"])
        script_output_folder = None
        if ok:
            ok, script_output_folder = get_string_or_environment_value(f"{output_path}/{self.experiment['title']}")
        if ok:
            ok = fs_ensure_folder_exists(output_path)
        if ok:
            ok = fs_ensure_folder_exists(script_output_folder)
        return ok, output_path, script_output_folder

    def env_expand(self, s):
        ok, val = get_string_or_environment_value(self.experiment["tool_path"])
        if ok:
            return s.replace("{experiment.tool_path}", val)
        error_out("TOOL path not set, exiting")


class Configuration:
    def __init__(self, experiment, configuration_yaml):
        self.experiment = experiment
        self.configuration = configuration_yaml

    def install(self):
        return self.configuration["install"]

    def run(self):
        return self.configuration["run"]

    def wait_until_started(self):
        return self.experiment.env_expand(self.configuration["wait_until_started"])

    def is_started(self):
        return self.experiment.env_expand(self.configuration["is_started"])
