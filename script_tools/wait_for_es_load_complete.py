import sys
import glob
import requests
import time
import json

processed_folder = sys.argv[1]
es_url = sys.argv[2]
es_index = sys.argv[3]

print(f"Waiting for Elasticsearch loading to complete")
print(f"   Processed folder: {processed_folder}")
print(f"   ES URL: {es_url}")
print(f"   ES index: {es_index}")

#
#  query Elasticsearch for total count, and species specific count
#
def es_count():
    response = requests.get( f"{es_url}/{es_index}/_count", headers={'content-type': 'application/json'} )
    es_response = json.loads(response.text)
    if 'count' in es_response:
        return es_response['count']
    else:
        return 0

expectedSpeciesCounts = {}
files = glob.glob(f"{processed_folder}/*.line_count")
for file in files:
    file_name = file.split("/")[-1]
    species = file_name.split(".")[0]
    with open(file, "r") as in_file:
        line = in_file.readline()
        data = line.split()
        line_count = int(data[0])
    expectedSpeciesCounts[species] = line_count

for species, count in expectedSpeciesCounts.items():
    print(f"Expecting {species} to have {count} records")

expectedTotalCount = sum(expectedSpeciesCounts.values())
print(f"Expecting total: {expectedTotalCount}")
try_counter = 0
while True:
    print(f"Checking record count in {es_url}/{es_index}")
    try_counter += 1
    count = es_count()
    if count == expectedTotalCount:
        print(f"\n\n\nSUCCESSFULLY LOADED {expectedTotalCount} records into Elasticsearch")
        break
    else:
        print(f"{count} of {expectedTotalCount} records loaded, sleep 5 seconds, and try again")
        time.sleep(5)

print(f"{try_counter} checks, {(try_counter-1)*5} seconds")
print("All records are loaded in Elasticsearch.")
print("Query script can now run to establish relationships between records.\n")