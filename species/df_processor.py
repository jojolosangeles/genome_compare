"""Functions for processing a DataFrame with best match for each segment/species

DataFrame columns listed below, only "score", "sloc", and "mloc" columns are 'int' data type

  Sample Data columns:

    sp - species providing the sample for the relationship search
    chr - the chromosome providing the sample
    sloc - sequence value offset in the chromosome providing the sample
    dsSO - byte offset of the first sequence value in the text file providing the data, suitable for fseek

  Matched Data columns:

    msp - species matched
    mchr - chromosome of the matched species
    mloc - sequence value offset in the matched chromosome
    score - score returned by Elasticsearch
    orientation -- orientation of the match
  """
import pandas as pd


def read_genome_comparison_csv(csvFile):
    """Return DataFrame for the CSV file that resulted from Elasticsearch scoring of relationships."""
    compression = "gzip" if csvFile.endswith(".gz") else None
    df = pd.read_csv(csvFile,
                     compression=compression,
                     index_col=False,
                     usecols=['sp', 'chr', 'sloc', 'score', 'msp', 'mchr', 'mloc', 'orientation', 'segsize'],
                     dtype={'sp': str, 'chr': str, 'sloc': int,
                            'score': int,
                            'msp': str, 'mchr': str, 'mloc': int,
                            'orientation': str, 'segsize': int, 'dsSO': int, 'dsEO': int})
    mean_score = int(df['score'].mean())
    return df[df['score'] > mean_score]

def confusion_matrix_data(df):
    return df.groupby(['sp', 'chr', 'msp', 'mchr'], as_index=False)['sloc'].count()

def species_to_species(df):
    cm_data = confusion_matrix_data(df)
    for sp in cm_data['sp'].unique():
        spdf = cm_data[cm_data['sp'] == sp]
        for msp in spdf['msp'].unique():
            yield sp, msp, spdf[spdf['msp'] == msp]

def confusion_matrix_generator(df):
    for sp, msp, mspdf in species_to_species(df):
        df_result = mspdf.groupby(['chr', 'mchr', 'sloc'], as_index=False).count().drop(['sp', 'msp'], axis=1)
        df_result['sp'] = sp
        df_result['msp'] = msp
        yield df_result

def inverse_range_generator(df):
    for sp, msp, mspdf in species_to_species(df):
        pass

