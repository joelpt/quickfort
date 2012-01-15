"""aliases.txt support."""

import re
import util


def load_aliases(filename):
    """
    Loads aliases.txt-formatted file and returns a dict.

    Accepted formats:
        aliasname,keystrokes    (QF1.x style)
        aliasname:keystrokes    (QF2.x style)
    """
    aliases = {}

    # load the file contents
    with open(filename) as f:
        data = f.read()

    data = util.convert_line_endings(data)
    lines = data.split('\n')

    # strip out comment and empty lines
    lines = [line for line in lines if line != '' and line[0] != '#']

    # break into {aliasname:keystrokes} pairs
    for line in lines:
        match = re.match(r'([\w\d]+)(,|:) *(.+)\s*\n*', line)
        if match is not None:
            aliases[match.group(1)] = match.group(3)

    return aliases


def apply_aliases(layers, aliases):
    """
    Applies aliases:dict(aliasname, keystrokes) to layers:[FileLayer].

    Every cell in every layer will be replaced with 'keystrokes' if
    it exactly matches 'aliasname'. Currently there is no support
    for having multiple aliases in a single cell or mixing aliases
    with regular keystrokes in a cell.
    """

    for layer in layers:
        for r, row in enumerate(layer.rows):
            for c, cell in enumerate(row):
                for alias in aliases.iterkeys():
                    if cell == alias:  # alias match
                        layer.rows[r][c] = aliases[alias]
    return layers
