"""
Example: python max_score.py --csv_folder /Users/johannesjohannsen/genomes/graph_data/6primates --max_csv_folder /Users/johannesjohannsen/genomes/graph_data/6primates_max

Genome processing scripts generate CSV match scores between genomes with these columns (CSV files have no header):

sp,chr,loc,score,msp,mchr,mloc,orientation,segsize,dsSO

sp -- name of species we are sampling
chr -- chromosome of the sampled species
loc -- location in the chromosome of the sampled species (in terms of sequence-only, ACGT offset)
segsize -- the size of the segment of data that is represented in a single Elasticsearch document.  Note, the
data in Elasticsearch is NOT the sequence data, but a sequence of text words generated from that data.

The sample is extracted from a part of this 'segsize' section of the sequence specified by the 'sp','chr','loc' values.
The sample size should be much smaller than the 'segsize', it is on mkdoit.py command line, test case for segsize 1M
uses 3 percent for the sample size.

The sample and it's inverse complement are both processed to get a sequence of text words, then Elasticsearch
searches through all genomes and returns scores and matches.

The rest of the column values are from these matching scores:

score -- Elasticsearch score of the matched location
msp -- the name of the species matched
mchr -- the name of the chromosome matched
mloc -- the location in the matched chromosome

dsSO -- the offset in the original text file containing the sequence data, for seeking to file location
in original unprocessed text data file.

------

This program takes processes the CSV search results, keeping only the maximum score record for
each matching species.

For each CSV file in the source folder, if there is NOT a corresponding CSV file in the dest folder,
the CSV file is read, a new DataFrame is created containing only the species matches with maximum scores,
and the new result is saved in a CSV file with the same name in the "max_csv_folder"
"""
import click
import glob, os
import pandas as pd


@click.command()
@click.option("--csv_folder",
              help="folder containing CSV files, each line:  sp,chr,loc,score,msp,mchr,mloc,orientation,segsize,dsSO")
@click.option("--max_csv_folder", help="folder containing CSV files with only max match to another species")
def process_csv_files(csv_folder, max_csv_folder):
    os.chdir(csv_folder)
    csv_files_to_process = glob.glob("*.csv")
    if not os.path.exists(max_csv_folder):
        print(f"PATH {max_csv_folder} does not exist, CREATING IT")
        os.mkdir(max_csv_folder)
    os.chdir(max_csv_folder)
    csv_files_already_processed = glob.glob("*.csv")

    def process_csv_file(in_file, out_file):
        df = pd.read_csv(in_file,
                         names=['sp', 'chr', 'loc', 'score', 'msp', 'mchr', 'mloc', 'orientation', 'segsize', 'dsSO', 'dsEO'],
                         index_col=False)
        idx = df.groupby(['loc', 'msp'])['score'].transform(max) == df['score']
        df[idx].to_csv(out_file)

    for file in csv_files_to_process:
        if file not in csv_files_already_processed:
            print(f"Processing: {file}")
            process_csv_file(os.path.join(csv_folder, file), os.path.join(max_csv_folder, file))
        else:
            print(f"..already processed: {file}")


if __name__ == "__main__":
    process_csv_files()
