from itertools import product
import pandas as pd


def load_df(csv_file):
    df = pd.read_csv(csv_file,
                     compression='infer',
                     index_col=False,
                     header=None,
                     names=['fkidx','sp','chr','segloc','score','msp','mchr','mloc','orientation','segsize'],
                     usecols=['sp','chr','segloc','score','msp','mchr','mloc','orientation','segsize'],
                     dtype={ 'sp': str, 'chr': str, 'segloc': int,
                             'score': int,
                             'msp': str, 'mchr': str, 'mloc': int,
                             'orientation': str, 'segsize': int, 'dsSO': int, 'dsEO': int })
    return df


def df_process(df):
    l1, l2 = df['sp'].unique(), df['sp'].unique()
    output = list(product(l1, l2))
    for sp,msp in output:
        spair_df = df[(df['sp'] == sp) & (df['msp'] == msp)]
        for chr in spair_df['chr'].unique():
            schr = spair_df[spair_df['chr'] == chr]
            for mchr,xdf in schr.groupby('mchr'):
                yield(sp,chr,msp,mchr,len(xdf))

def related_chromosome_df(df):
    return pd.DataFrame(df_process(df), columns=['sp','chr','msp','mchr','count'])