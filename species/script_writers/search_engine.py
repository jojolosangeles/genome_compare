from experiment import Experiment, Configuration, error_out
from contextlib import contextmanager
import os


def script(outFile, comment, command):
    outFile.write("#\n")
    if not command:
        outFile.write(f"# SKIPPING, not configured: {comment}")
    else:
        outFile.write(f"# {comment}\n")
        outFile.write("#\n")
        outFile.write(f"{command}\n")
    outFile.write("#\n")


class Condition:
    def __init__(self, script_name, output_file):
        self.script_name = script_name
        self.output_file = output_file

    @contextmanager
    def not_condition(self):
        try:
            self.output_file.write(f"cmd=\"{self.script_name}\"\n")
            self.output_file.write("result=`${cmd}`\n")
            self.output_file.write("if [ $? != 0 ]; then\n")
            yield self
        finally:
            self.output_file.write("fi\n")


def search_engine_script(script_output_folder, experiment, configuration):
    output_file_path = f"{script_output_folder}/search_engine.sh"
    if os.path.isfile(output_file_path):
        print(f"SKIPPING search_engine script generation, script {output_file_path} already exists")
    else:
        print(f"Writing search_engine script to {output_file_path}")
        with open(f"{output_file_path}", "w") as outFile:
            outFile.write(f"# {experiment.timestamp}, generated by script_writer.py\n")

            with Condition(configuration.is_started(), outFile).not_condition():
                script(outFile, "Install the search engine", configuration.install())
                script(outFile, "Run the search engine", configuration.run())

            script(outFile, "Wait for search engine to start", configuration.wait_until_started())
            outFile.write("# END OF GENERATED SCRIPT")


def search_engine_loader_script(script_output_folder, experiment, configuration):
    output_file_path = f"{script_output_folder}/search_engine_loader.sh"
    if os.path.isfile(output_file_path):
        print(f"SKIPPING search engine loader script, script {output_file_path} already exists")
    else:
        print(f"Writing search engine LOADER script: {output_file_path}")
        with open(f"{output_file_path}", "w") as outFile:
            outFile.write(f"# {experiment.timestamp}, generated by script_writer.py\n")

            with Condition(configuration.is_started(), outFile).not_condition():
                script(outFile, "Install the search engine loader", configuration.install())
                script(outFile, "Configure the loader", configuration.configure())
                script(outFile, "Run the search engine loader", configuration.run())

            outFile.write("# END OF GENERATED SCRIPT")