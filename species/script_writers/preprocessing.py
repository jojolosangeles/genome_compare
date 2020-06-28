from experiment import Configuration, Transformations, error_out
import os


def preprocessing_script(script_output_folder, experiment, configuration, transformations):
    ok, input_data = experiment.input_data_specification()
    if not ok:
        error_out(f"Could not load input data specification")
    segment_size = configuration.segment_size()
    min_word_length = transformations.min_word_length()
    target_folder = experiment.target_folder()
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
            for line in lines:
                species, chromosome, filePath = line.strip().split()
                species_set.add(species)
                outFile.write(f"python processing.py {species} {chromosome} {filePath} {segment_size} ")
                outFile.write(f"{min_word_length} {target_folder}/{experiment.title()} {sample_size_percent} {number_samples}")
                outFile.write("\n")
                # optional additional parameters: {ndel} {ndellen}")

            # these are check against elasticsearch record counts (once logstash has loaded those -- how can we tell it
            # is done?)
            for species in species_set:
                outFile.write(f"cat {target_folder}/{experiment.title()}/processed/{species}.*.processed | wc > {target_folder}/{species}.line_count\n")