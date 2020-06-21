import yaml
import sys
import os.path
from search_engine import search_engine_script

if len(sys.argv) != 2:
    print("Usage: python script_write.py <path-to-config-file>")
    exit(0)

filePath = sys.argv[1]
if not os.path.isfile(filePath):
    print(f"'{filePath}' not found")
    exit(0)

with open(filePath) as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

    search_engine_script(config["experiment"], config["search_engine"])
