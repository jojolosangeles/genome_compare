import click
import os

@click.command()
@click.option("--section-size", type=int, help="size of each searchable section")
@click.option("--target-folder", help="folder to contain resulting data")
@click.option("--data-files", help="text file, listing of source data files and their metadata: <species>,<chromosome>,<datafile>")
@click.option("--processing-config", default="config/config.test", help="line and list processing before elasticsearch gets data")
@click.option("--search-size", type=float, help="proportion of section to use for a search term, e.g. '.01'")
@click.option("--target-index", help="elasticsearch index to contain genome data")

# lines = open("files2.txt", "r").readlines()
# LINE_GEN = "python ../line_gen.py --datasource FILEPATH --linelen 1000000 --outfile esdata/SPECIES_CHROMOSOME.1m --filter \"len(line) == 0 or line[0] == '>'\""
#
# line_modification = "line.replace('CG', 'C G').replace('GC', 'G C').replace('AT', 'A T').replace('TA', 'T A').replace('N', '')"
# list_modification =  "[val for val in data if len(val) > 5]"
# dest_index = "cgh_genomes"
# #line_modification = "line.replace('CG', 'C G').replace('GC', 'G C').replace('AA', 'A A').replace('TT', 'T T').replace('N', '')"
# #list_modification =  "[val for val in data if len(val) > 10]"
#
# MK50 = "python ../mk50.py esdata/SPECIES_CHROMOSOME.1m.es_bulk"
#
# print("set -x")
# for line in lines:
#   line = line.strip()
#   species,chromosome,filepath = line.split()
#   print(LINE_GEN.replace("FILEPATH", filepath).replace("SPECIES", species).replace("CHROMOSOME", chromosome))
#   print(ES_GEN.replace("SPECIES", species).replace("CHROMOSOME", chromosome))
#   print(MK50.replace("SPECIES", species).replace("CHROMOSOME", chromosome))

def gen_script(section_size, target_folder, data_files, processing_config, search_size, target_index):
    ES_GEN = f"python esgen.py --datasource {target_folder}/SPECIES.CHROMOSOME.{section_size}  --chromosome CHROMOSOME --species SPECIES --index {target_index} --processing-config {processing_config} --idprefix SPECIES_CHROMOSOME --outfile {target_folder}/SPECIES.CHROMOSOME.{section_size}.es_bulk"
    number_lines = int(50000000/section_size)*2  # approximate
    MK50 = f"python mk50.py {target_folder}/SPECIES.CHROMOSOME.{section_size}.es_bulk {number_lines}"
    MKLOAD = f"python mkload.py {target_folder}/SPECIES.CHROMOSOME.{section_size}.es_bulk > {target_folder}/load_SPECIES_CHROMOSOME"
    # make it visible
    print("set -x")

    # make sure target folder exists
    print(f"mkdir -p {target_folder}")

    # get the list of files to process
    lines = open(data_files, "r").readlines()

    # for processing a single file
    def process_file(species, chromosome, filepath, section_size):
        # generate sections of data as a sequence of lines of text
        target_file = f"{target_folder}/{species}.{chromosome}.{section_size}"
        print(f"python line_gen.py --datasource {filepath} --linelen {section_size} --outfile {target_file} --filter \"len(line) == 0 or line[0] == '>'\"")
        print(ES_GEN.replace("SPECIES", species).replace("CHROMOSOME", chromosome))
        print(MK50.replace("SPECIES", species).replace("CHROMOSOME", chromosome))
        print(MKLOAD.replace("SPECIES", species).replace("CHROMOSOME", chromosome))
        print(f"chmod +x {target_folder}/load_{species}_{chromosome}")
        print(f"./{target_folder}/load_{species}_{chromosome}")

    for line in lines:
        line = line.strip()
        species, chromosome, filepath = line.split()
        process_file(species, chromosome, filepath, section_size)

if __name__ == "__main__":
    gen_script()