"""Intersects two minecraft schematics, provided they are the same size.
"""

import argparse
import json
import os
import shutil
import subprocess
import tempfile

from io import TextIOWrapper
from pathlib import Path
from typing import Dict, List, Tuple

class Options(argparse.Namespace): # pylint: disable=too-few-public-methods
    """Program options
    """

    nbt2json_path: str = Path(os.path.dirname(os.path.realpath(__file__))) / 'nbt2json'
    inputs: Tuple[Dict, Dict]
    outfile: str

class LoadInfiles(argparse.Action): # pylint: disable=too-few-public-methods
    """Custom action for infile arguments to load their json
    """

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(
            namespace,
            self.dest,
            tuple(
                json.loads(
                    subprocess.run(
                        ['nbt2json.exe', '--java'],
                        cwd=Options.nbt2json_path,
                        shell=True,
                        stdin=infile,
                        stdout=subprocess.PIPE,
                        text=True,
                        check=True
                    ).stdout
                ) for infile in values[:self.nargs]
            )
        )

def get_options() -> Options:
    """Defines and retrieves program options

    Returns:
        Options -- Program options
    """

    parser = argparse.ArgumentParser(
        description='Intersects two minecraft schematics, provided they are the same size.'
    )
    parser.add_argument(
        'inputs',
        help='Input schematic file',
        nargs=2,
        type=argparse.FileType('r'),
        default=None,
        metavar='infile',
        action=LoadInfiles
    )
    parser.add_argument(
        'outfile',
        help='Output schematic file. Intersecting blocks will be cobblestone.',
        default=None
    )

    options: Options = parser.parse_args(namespace=Options)

    # Check dimensions
    input_dimensions: Tuple[Dict, Dict] = tuple(
        { # pylint: disable=unsubscriptable-object
            obj['name']: obj['value'] for obj in input['nbt'][0]['value'] if obj['tagType'] == 2
        } for input in options.inputs[:2]
    )

    if input_dimensions[0] != input_dimensions[1]:
        parser.error('Input schematics have different dimensions.')

    return options

def get_blocks_or_data(json_object: Dict, name: str) -> List[int]:
    """Get array of blocks or data from schematic json

    Arguments:
        json_object {Dict} -- Schematic json
        name {str} -- 'Blocks' or 'Data'

    Returns:
        List[int] -- Array of values
    """

    return [obj['value'] for obj in json_object['nbt'][0]['value'] if obj['name'] == name][0]

def get_blocks(json_object: Dict) -> List[int]:
    """Get array of blocks from schematic json

    Arguments:
        json_object {Dict} -- Schematic json

    Returns:
        List[int] -- Array of block values
    """

    return get_blocks_or_data(json_object, 'Blocks')

def get_data(json_object: Dict) -> List[int]:
    """Get array of data from schematic json

    Arguments:
        json_object {Dict} -- Schematic json

    Returns:
        List[int] -- Array of data values
    """

    return get_blocks_or_data(json_object, 'Data')

def intersect(input_blocks: Tuple[int, int]) -> int:
    """Intersect tuple of input blocks to return air or stone

    Arguments:
        input_blocks {Tuple[int, int]} -- Two input blocks

    Returns:
        int -- Intersected block
    """

    if input_blocks[0] == 0 or input_blocks[1] == 0:
        return 0
    return 4

def main():
    """Main function
    """

    options: Options = get_options()

    # Deep-copy the output from the first input
    output: Dict = json.loads(json.dumps(options.inputs[0]))

    # Zero the block data
    output_data: List[int] = get_data(output)
    for index, _ in enumerate(output_data):
        output_data[index] = 0

    # Replace intersecting blocks with cobblestone
    intput_blocks = zip(get_blocks(options.inputs[0]), get_blocks(options.inputs[1]))
    output_blocks: List[int] = get_blocks(output)
    for index, blocks in enumerate(intput_blocks):
        output_blocks[index] = intersect(blocks)

    # Turn the intersected output back into a schematic
    with tempfile.NamedTemporaryFile('w', delete=False) as temp_outfile:
        subprocess.run(
            ['nbt2json.exe', '--reverse', '--java'],
            cwd=options.nbt2json_path,
            shell=True,
            input=json.dumps(output),
            stdout=temp_outfile,
            text=True,
            check=True
        ).check_returncode()
    shutil.copyfile(temp_outfile.name, options.outfile)
    os.remove(temp_outfile.name)

if __name__ == "__main__":
    main()
