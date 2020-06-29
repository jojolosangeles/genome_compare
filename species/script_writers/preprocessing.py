from experiment import error_out
import os


def preprocessing_script(script_output_folder, experiment, configuration, transformations):
    ok, input_data = experiment.input_data_specification()
    if not ok:
        error_out(f"Could not load input data specification")
    segment_size = configuration.segment_size()
    min_word_length = transformations.min_word_length()
    target_folder = experiment.target_folder()
    tool_folder = experiment.tool_folder()
    number_samples, sample_size_percent = configuration.sample_size_info()

    output_file_path = f"{script_output_folder}/preprocessing.sh"
    if os.path.isfile(output_file_path):
        print(f"SKIPPING preprocessing script generation, script {output_file_path} already exists")
    else:
        print(f"Writing preprocessing script to {output_file_path}")

        with open(f"{output_file_path}", "w") as outFile, open(input_data) as inFile:
            lines = inFile.readlines()
            outFile.write(f"mkdir -p {target_folder}/{experiment.title()}/processed\n")
            outFile.write(f"mkdir -p {target_folder}/{experiment.title()}/samples\n")
            species_set = set()
            counter = 0
            total = len(lines)
            for line in lines:
                counter += 1
                species, chromosome, filePath = line.strip().split()
                species_set.add(species)
                outFile.write(f"echo 'processing file {filePath} ({counter} of {total})'\n")
                outFile.write(f"python {tool_folder}/processing.py {species} {chromosome} {filePath} {segment_size} ")
                outFile.write(f"{min_word_length} {target_folder}/{experiment.title()} {sample_size_percent} {number_samples}")
                outFile.write("\n")
                # optional additional parameters: {ndel} {ndellen}")

            outFile.write("#\n")
            outFile.write("# count of expected elasticsearch records per species\n")
            outFile.write("#\n")
            for species in species_set:
                processed_path = f"{target_folder}/{experiment.title()}/processed"
                outFile.write(f"cat {processed_path}/{species}.*.processed | wc > {processed_path}/{species}.line_count\n")


def query_with_samples(script_output_folder, experiment, configuration):
    output_file_path = f"{script_output_folder}/query_samples.sh"
    tool_folder = experiment.tool_folder()
    processed_folder = experiment.processed_folder()
    if os.path.isfile(output_file_path):
        print(f"SKIPPING sample_query script generation, script {output_file_path} already exists")
    else:
        print(f"Writing preprocessing script to {output_file_path}")
        with open(f"{output_file_path}", "w") as outFile:
            outFile.write("#\n")
            outFile.write("# wait for elasticsearch load to complete\n")
            outFile.write("#\n")
            outFile.write(f"python {tool_folder}/wait_for_es_load_complete.py {processed_folder} {experiment.elasticsearch_url()} {experiment.title()}\n")

            outFile.write("#\n")
            outFile.write("# generate the query script\n")
            outFile.write("#\n")

            run_queries_script_path = f"{script_output_folder}/run_queries.sh"
            outFile.write(
                f"python {tool_folder}/generate_query_script.py \"{configuration.sample_file_pattern()}\" {experiment.title()} {tool_folder} {experiment.elasticsearch_url()}  > {run_queries_script_path}\n")
            outFile.write(f"chmod +x {run_queries_script_path}\n")
            outFile.write(f"{run_queries_script_path}\n")
