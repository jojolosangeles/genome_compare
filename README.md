# Genome Comparison

Input:  Directory with one sub-directory per species, one FASTA file per chromosome

DataFrame Output:  
- Confusion matrix for each species-to-species comparison
- Inversions and Translocations between related species

Graph Output:
- Confusion matrix for each species-to-species comparison
- Inversions and Translocations for related chromosomes across species

#### Step 1: put FASTA data files into a folder structure like this:
```
base directory
  |
  +--- species 1 directory
  |      |
  |      + chromosome 1 FASTA file
  |      + chromosome 2 FASTA file
  |      ...
  |
  +--- species 2 directory
  |      |
  |      + chromosome 1 FASTA file
  |      + chromosome 2 FASTA file
  ...    ...

```

### Step 2:  for a given configuration, create output artifacts

Generate, then run a script.  A default configuration file is provided listing options,
only the base folder option is required (see default.config for details)

```
python related_species.py --config PATH_TO_CONFIGURATION
PATH_TO_CONFIGURATION/relate_species.sh
```

### Step 3:  check status from static site
```
open PATH_TO_CONFIGURATION/_website/index.html
```

-----

The generated script can be stopped at any time and restarted, it will recover from
any issues related to an unexpected stop/restart.

