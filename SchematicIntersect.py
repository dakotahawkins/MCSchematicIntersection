"""Intersects two minecraft schematics, provided they are the same size.
"""

import argparse
import json
import os
import subprocess

from pathlib import Path

SCRIPTDIR = os.path.dirname(os.path.realpath(__file__))

PARSER = argparse.ArgumentParser(
    description='Intersects two minecraft schematics, provided they are the same size.'
)
PARSER.add_argument(
    'infile',
    help='Input schematic file',
    nargs=2,
    type=argparse.FileType('r'),
    default=None
)
PARSER.add_argument(
    'outfile',
    help='Output schematic file. Intersecting blocks will be cobblestone.',
    type=argparse.FileType('w'),
    default=None
)

class Options: # pylint: disable=too-few-public-methods
    """Options class
    """
OPTIONS = Options()
PARSER.parse_args(namespace=OPTIONS)

INPUT_A = json.loads(subprocess.run(
    ['nbt2json.exe', '--java'],
    cwd=Path(SCRIPTDIR) / 'nbt2json',
    shell=True,
    stdin=OPTIONS.infile[0], # pylint: disable=no-member
    stdout=subprocess.PIPE,
    text=True,
    check=True
).stdout)
INPUT_B = json.loads(subprocess.run(
    ['nbt2json.exe', '--java'],
    cwd=Path(SCRIPTDIR) / 'nbt2json',
    shell=True,
    stdin=OPTIONS.infile[1], # pylint: disable=no-member
    stdout=subprocess.PIPE,
    text=True,
    check=True
).stdout)

A_DIMENSIONS = {
    obj['name']: obj['value'] for obj in INPUT_A['nbt'][0]['value'] if obj['tagType'] == 2
}
B_DIMENSIONS = {
    obj['name']: obj['value'] for obj in INPUT_B['nbt'][0]['value'] if obj['tagType'] == 2
}

if A_DIMENSIONS != B_DIMENSIONS:
    PARSER.error('Input schematics have different dimensions.')

OUTPUT = json.loads(json.dumps(INPUT_A))

def get_blocks_or_data(json_object, name):
    """Get array of blocks or data from schematic json

    Arguments:
        json_object {dict} -- Schematic json
        name {str} -- 'Blocks' or 'Data'

    Returns:
        [int] -- Array of values
    """

    return [obj['value'] for obj in json_object['nbt'][0]['value'] if obj['name'] == name][0]

def get_blocks(json_object):
    """Get array of blocks from schematic json

    Arguments:
        json_object {dict} -- Schematic json

    Returns:
        [int] -- Array of block values
    """

    return get_blocks_or_data(json_object, 'Blocks')

def get_data(json_object):
    """Get array of data from schematic json

    Arguments:
        json_object {dict} -- Schematic json

    Returns:
        [int] -- Array of data values
    """

    return get_blocks_or_data(json_object, 'Data')

# Zero the block data
OUTPUT_DATA = get_data(OUTPUT)
for index, d in enumerate(OUTPUT_DATA):
    OUTPUT_DATA[index] = 0

def intersect(input_blocks):
    """Intersect tuple of input blocks to return air or stone

    Arguments:
        input_blocks {(int)} -- Two input blocks

    Returns:
        int -- Intersected block
    """

    if input_blocks[0] == 0 or input_blocks[1] == 0:
        return 0
    return 4

# Replace intersecting blocks with stone
OUTPUT_BLOCKS = get_blocks(OUTPUT)
for index, blocks in enumerate(zip(get_blocks(INPUT_A), get_blocks(INPUT_B))):
    OUTPUT_BLOCKS[index] = intersect(blocks)

subprocess.run(
    ['nbt2json.exe', '--reverse', '--java'],
    cwd=Path(SCRIPTDIR) / 'nbt2json',
    shell=True,
    input=json.dumps(OUTPUT),
    stdout=OPTIONS.outfile, # pylint: disable=no-member
    text=True,
    check=True
)
