"""Tests two schematic json files to ensure they're equal
"""

import json
import sys

INPUT_A: str = sys.argv[1]
INPUT_B: str = sys.argv[2]

with open(INPUT_A, 'r') as infile_a:
    with open(INPUT_B, 'r') as infile_b:
        if json.load(infile_a)['nbt'] != json.load(infile_b)['nbt']:
            sys.exit(1)
sys.exit(0)
