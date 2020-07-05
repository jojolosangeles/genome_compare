import os


def relate_chromosomes(script_output_folder, experiment, configuration):
    output_file_path = f"{script_output_folder}/relate_chromosomes.sh"
    tool_folder = experiment.tool_folder()
    if os.path.isfile(output_file_path):
        print(f"SKIPPING relate_chromosomes script generation, script {output_file_path} already exists")
    else:
        print(f"Writing relate_chromosomes script to {output_file_path}")
        with open(f"{output_file_path}", "w") as outFile:
            outFile.write("#\n")
            outFile.write("# combine samples, summarize\n")
            outFile.write("#\n")
            outFile.write(f"{configuration.prepare()}\n")
            for line in configuration.summarize():
                outFile.write(f"{line}\n")
