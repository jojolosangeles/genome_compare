import sys

filePath = sys.argv[1]
targetFolder = sys.argv[2]
species = sys.argv[3]
chromosome = sys.argv[4]
sectionSize = int(sys.argv[5])
searchSize = int(sys.argv[6])
target_index = sys.argv[7]

lines = open(filePath, "r").readlines()

def comp(val):
    if val == 'A':
        return 'T'
    elif val == 'C':
        return 'G'
    elif val == 'G':
        return 'C'
    elif val == 'T':
        return 'A'
    else:
        return val


def revcomp(s):
    l = [comp(v) for v in reversed(s)]
    return "".join(l)

for line_number, line in enumerate(lines):
    location = line_number * sectionSize
    if len(line) > searchSize:
        # write the data files referenced by search script
        search_data = line[:searchSize]
        dataFile = f"{targetFolder}/{species}.{chromosome}.{line_number*sectionSize}"
        with open(dataFile, "w") as searchData:
            searchData.write(f"data is {search_data}\n")
        revcompDataFile = f"{dataFile}.revcomp"
        with open(revcompDataFile, "w") as revcmpSearchData:
            revcmpSearchData.write(f"data is {revcomp(search_data)}")

        # write the search script
        print(f"python jjquery.py --query {dataFile} --index {target_index} > {dataFile}.json")
        print(f"python jjquery.py --query {revcompDataFile} --index {target_index} > {revcompDataFile}.json")
