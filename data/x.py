import click

@click.command()
@click.option("--source", prompt="Source data file", help="Source data file")
@click.option("--record", type=int, prompt="Record number", help="Record number")
@click.option("--entry", type=int, help="<entry> of <num_entries>")
@click.option("--num_entries", type=int, help="<entry> of <num_entries>")

def do_search(source, record, entry, num_entries):
    with open(source, "r") as inFile:
        lines = inFile.readlines()
        number_lines = len(lines)
        line_offset = record * 2 + 1
        if line_offset < number_lines:
            data = lines[line_offset].split("\"")
            SEQ_OFFSET = 7
            CHROMOSOME_OFFSET = 11
            SPECIES_OFFSET = 15
            sequence = data[SEQ_OFFSET]
            species = data[SPECIES_OFFSET]
            chromosome = data[CHROMOSOME_OFFSET]
            entries = sequence.split()
            print(f"# number entries: {len(entries)}, species: {species}, chromosome: {chromosome}")
            entries_per_group = int(len(entries)/num_entries)
            print(f"# entries_per_group {entries_per_group}")
            firstOffset = entries_per_group*entry
            lastOffset = entries_per_group*(entry+1)
            print(f"# firstOffset {firstOffset}, lastOffset {lastOffset}")
            s = " ".join(entries[entries_per_group*entry:entries_per_group*(entry+1)])

            print(f"# species={species},chromosome={chromosome}")
            print(f"data is {sequence}")
        else:
            print(f"# bad record {record}, gives line_offset {line_offset}, but number_lines is {number_lines}")


if __name__ == "__main__":
    do_search()
