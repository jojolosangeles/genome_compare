"""
alias ipython='ipython -i ipython_startup.py'

code to be executed when started from this folder
"""
import pandas as pd
import numpy as np

pd.options.mode.chained_assignment = None

data_dir = "/Users/johannesjohannsen/genomes/graph_data/6primates_max"

print(f"\n\nUSING data_dir={data_dir}")
print("\n\nFunctions defined:\n")
print("sp_chr_df(sp, chr) returns df")
print("get_matching_species_grouped_by_chromsome(df, species) returns DataFrameGroupBy")
print("df_chr(groups,chrval) returns data frame for that specific chrval")


def sp_chr_df(sp, chr):
    csvFile = f"{data_dir}/{sp}.{chr}.1000000.13.samples.csv"
    df = pd.read_csv(csvFile)
    return df


def get_matching_species_grouped_by_chromosome(df, species):
    msp = df[df['msp'] == species]
    return msp.groupby('mchr')


# where 'groups' are return value from 'get_matching_species_grouped_by_chromosoem' above
def df_chr(groups, chrval):
    for name, g in groups:
        if str(name) == str(chrval):
            return g
    return None


def df_sequences(df, meanval):
    return [name for name, g in df.groupby(['seq']) if len(g) > 1 and g.diff_mloc.mean() == meanval]


class Species:
    def __init__(self, name, resolution=1000000):
        self.name = name
        self.resolution = resolution

    def df_chr(self, chr):
        csvFile = f"{data_dir}/{self.name}.{chr}.{self.resolution}.13.samples.csv"
        df = pd.read_csv(csvFile)
        return df

    def df_msp(self, chr, matched_species):
        df = self.df_chr(chr)
        msp = df[df['msp'] == matched_species.name]
        for matched_chr_name, group in msp.groupby('mchr'):
            if str(matched_chr_name) == str(chr):
                return self.analyze(group)
        return None

    def analyze(self, df):
        series = df['loc'] / self.resolution
        df.loc[:, 'diff_loc'] = series.diff()
        series = df['mloc'] / self.resolution
        df.loc[:, 'diff_mloc'] = series.diff()
        not_in_sequence = ((df['diff_mloc'] != 1.0) & (df['diff_mloc'] != -1.0))
        df.loc[not_in_sequence, 'diff_mloc'] = 0
        df['seq'] = df['diff_mloc'].ne(df['diff_mloc'].shift()).cumsum()
        return df, df_sequences(df, 1.0), df_sequences(df, -1.0)


gorilla = Species("Gorilla_gorilla")
mf = Species("Macaca_fascicularis")
mmul = Species("Macaca_mulatta")
chimp = Species("Pan_troglodytes")
human = Species("hg38")
pongo = Species("Pongo_abelii")
