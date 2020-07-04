from df_process import load_df, related_chromosome_df
import sys

data_file = sys.argv[1]
out_file = sys.argv[2]

df = load_df(data_file)
rcdf = related_chromosome_df(df)
rcdf.to_csv(out_file, compression='gzip', index=False)