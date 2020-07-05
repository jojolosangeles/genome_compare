from itertools import product, combinations
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn
import sys
import os

ordering = {
    "Gorilla_gorilla": ['1', '2A', '2B', '3', '4', '5', '6', '7', '8', '9', '10',
                        '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
                        '21', '22', 'X'],
    "hg38": ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
             '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
             '21', '22', 'X', 'Y'],
    "Macaca_fascicularis": ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
                            '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
                            '21', '22', 'X'],
    "Macaca_mulatta": ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
                       '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
                       '21', '22', 'X', 'Y'],
    "Pan_troglodytes": ['1', '2A', '2B', '3', '4', '5', '6', '7', '8', '9', '10',
                        '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
                        '21', '22', 'X', 'Y'],
    "Pongo_abelii": ['1', '2A', '2B', '3', '4', '5', '6', '7', '8', '9', '10',
                     '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
                     '21', '22', 'X']
}


def load_df(csv_file):
    df = pd.read_csv(csv_file,
                     compression='infer',
                     index_col=False,
                     header=None,
                     names=['fkidx', 'sp', 'chr', 'segloc', 'score', 'msp', 'mchr', 'mloc', 'orientation', 'segsize'],
                     usecols=['sp', 'chr', 'segloc', 'score', 'msp', 'mchr', 'mloc', 'orientation', 'segsize'],
                     dtype={'sp': str, 'chr': str, 'segloc': int,
                            'score': int,
                            'msp': str, 'mchr': str, 'mloc': int,
                            'orientation': str, 'segsize': int, 'dsSO': int, 'dsEO': int})
    return df


def df_process(df):
    l1, l2 = df['sp'].unique(), df['sp'].unique()
    output = list(product(l1, l2))
    for sp, msp in output:
        spair_df = df[(df['sp'] == sp) & (df['msp'] == msp)]
        for chr in spair_df['chr'].unique():
            schr = spair_df[spair_df['chr'] == chr]
            for mchr, xdf in schr.groupby('mchr'):
                yield (sp, chr, msp, mchr, len(xdf))


def related_chromosome_df(df):
    return pd.DataFrame(df_process(df), columns=['sp', 'chr', 'msp', 'mchr', 'count'])


def vals(cdf, row_labels, col_labels):
    result = np.zeros(len(row_labels), int)
    for index, row in cdf.iterrows():
        if row['chr'] in row_labels:
            result[row_labels.index(row['chr'])] = int(row['count'])
    return result


def gen_graph(df, sp, msp, out_directory):
    sp_labels = ordering[sp]
    msp_labels = ordering[msp]

    out_file = f"{out_directory}/{sp}_vs_{msp}.png"
    print(f"  generate {out_file}")
    cm_df = df[(df['sp'] == sp) & (df['msp'] == msp)]
    print(cm_df)
    # creating a DataFrame with rows from sp, columns from msp
    # first create a dictionary with keys from msp, these will be the columns
    d = {key: vals(cm_df[cm_df['mchr'] == key], sp_labels, msp_labels) for key in msp_labels}
    d = {}
    for key in msp_labels:
        xdf = cm_df[cm_df['mchr'] == key]
        print(xdf)
        v = vals(xdf, sp_labels, msp_labels)
        print(v)
        d[key] = v
    ddf = pd.DataFrame(d)
    ddf.index = sp_labels
    print(ddf)

    fig, ax = plt.subplots(figsize=(10, 10))
    seaborn.heatmap(ddf, linecolor='#3f3151', linewidth=0.5, xticklabels=msp_labels, yticklabels=sp_labels,
                    cbar=False, annot=True, fmt='d')
    plt.yticks(rotation=0)
    plt.ylabel(sp, fontsize='large', fontweight='bold')
    plt.xlabel(msp, fontsize='large', fontweight='bold')
    plt.title(f"Chromosome Relationships", fontstyle='italic')
    plt.savefig(f"{out_file}")


def gen_chromosome_graphs(in_file, out_directory):
    df = pd.read_csv(in_file)
    chr_series = df['chr'].apply(lambda x: x.upper())
    mchr_series = df['mchr'].apply(lambda x: x.upper())
    df.insert(0, 'hsf', chr_series)
    df = df.drop('chr', axis=1)
    df = df.rename(columns={"hsf": "chr"})
    df.insert(0, 'hsf', mchr_series)
    df = df.drop('mchr', axis=1)
    df = df.rename(columns={"hsf": "mchr"})
    df = df.astype({"count": int})
    species = df['sp'].unique()
    for sp1, sp2 in combinations(species, 2):
        gen_graph(df, sp1, sp2, out_directory)
        gen_graph(df, sp2, sp1, out_directory)


if __name__ == "__main__":
    in_file = sys.argv[1]
    out_directory = sys.argv[2]
    if not os.path.exists(out_directory):
        print(f"PATH {out_directory} does not exist, CREATING IT")
        os.mkdir(out_directory)
    gen_chromosome_graphs(in_file, out_directory)
