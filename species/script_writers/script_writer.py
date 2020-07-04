import yaml
import sys
import os.path
from search_engine import search_engine_script, search_engine_loader_script
from preprocessing import preprocessing_script, query_with_samples
from relationships import relate_chromosomes
from experiment import Experiment, Configuration, Transformations, error_out

if len(sys.argv) != 2:
    print("Usage: python script_write.py <path-to-config-file>")
    exit(0)

filePath = sys.argv[1]
if not os.path.isfile(filePath):
    print(f"'{filePath}' not found")
    exit(0)

with open(filePath) as file:
    config = yaml.load(file, Loader=yaml.FullLoader)
    experiment = Experiment(config["experiment"])

    ok, output_path, script_output_folder = experiment.get_output_folders()
    if not ok:
        error_out(f"Output folders not available: {output_path}, {script_output_folder}")
    preprocessing_script(script_output_folder, experiment,
                         Configuration(experiment, config["preprocessing"]),
                         Transformations(config["transformations"]))
    search_engine_script(script_output_folder, experiment,
                         Configuration(experiment, config["search_engine"]))
    search_engine_loader_script(script_output_folder, experiment,
                                Configuration(experiment, config["search_engine_loader"]))
    query_with_samples(script_output_folder, experiment,
                       Configuration(experiment, config["query_with_samples"]))
    relate_chromosomes(script_output_folder, experiment,
                       Configuration(experiment, config["relate_chromosomes"]))
