import click
import os.path

from os import path

@click.command()
@click.option("--species", prompt="species data source", help="species data source")
@click.option("--chromosome", prompt="chromosome data source", help="chromosome data source")
@click.option("--offset", type=int, prompt="offset into sequence", help="offset into sequence")
@click.option("--length", type=int, help="length of sequence to extract")

#(es_genome) (base) Johs-MacBook-Pro:data jojo$ python x.py --source esdata/chimp_5.1m.es_bulk.2 --record 13 --entry 1 --num_entries 2 --listmod "" > s1.txt

def do_search(species, chromosome, offset, length):
    def comp(val):
        if val == 'A':
            return 'T'
        elif val == 'C':
            return 'G'
        elif val == 'G':
            return 'C'
        else:
            return 'A'

    def revcomp(s):
        l = [comp(v) for v in s]
        return "".join(l)

    sourceFile = f"esdata/{species}_{chromosome}.1m.es_bulk"
    if not path.exists(sourceFile):
        print(f"File {sourceFile} not found")
        return
    with open(sourceFile, "r") as inFile:
        lines = inFile.readlines()
        number_lines = len(lines)
        line_offset = int(offset/1000000) * 2 + 1
        if line_offset < number_lines:
            data = lines[line_offset].split("\"")
            SEQ_OFFSET = 7
            CHROMOSOME_OFFSET = 11
            SPECIES_OFFSET = 15
            sequence = data[SEQ_OFFSET]
            species = data[SPECIES_OFFSET]
            chromosome = data[CHROMOSOME_OFFSET]
            print(f"# length of sequence: {len(sequence)}")
            print(f"# offset of sample: {offset}")
            print(f"# length of sample: {length}")
            print(f"# species={species},chromosome={chromosome}")
            print(f"data is {sequence[:length]}")
        else:
            print(f"# bad offset {offset}, results in line_offset {line_offset}, but number_lines is {number_lines}")


if __name__ == "__main__":
    do_search()
