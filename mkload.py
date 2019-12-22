import glob
import sys

basePath = sys.argv[1]
files = glob.glob(f"{basePath}.*")
for x in files:
    print(f"curl -H \"Content-Type: application/json\" -XPOST http://localhost:9200/_bulk --data-binary \"@{x}\"")
