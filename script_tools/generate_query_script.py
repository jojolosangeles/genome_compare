import sys
import glob

sample_file_pattern = sys.argv[1]
index = sys.argv[2]
tool_path = sys.argv[3]
elasticsearch_url = sys.argv[4]

files_to_process = glob.glob(sample_file_pattern)

print(f"# Sample File Pattern '{sample_file_pattern}'")
print(f"# .. found {len(files_to_process)} files to process")

total = len(files_to_process)
counter = 0
for file in files_to_process:
    counter += 1
    print(f"echo 'generate \"{file}.csv\" ({counter} of {total})'")
    print(f"python {tool_path}/sample_query.py --esurl {elasticsearch_url} --query {file} --index {index} > {file}.csv")
