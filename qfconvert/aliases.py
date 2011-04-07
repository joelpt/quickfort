"""aliases.txt support."""

import re

def load_aliases(filename):
    """
    Loads aliases.txt-formatted file and returns a dict.

    Accepted formats:
        aliasname,keystrokes    (QF1.x style)
        aliasname:keystrokes    (QF2.x style)
    """
    aliases = {}
    with open(filename) as f:
        lines = f.readlines()
    
    # strip out comment lines
    lines = [line for line in lines if line[0] != '#']

    # break into alias,keystroke pairs
    for line in lines:
        match = re.match(r'([\w\d]+)(,|:) *(.+)', line)
        if match is not None:
            aliases[match.group(1)] = match.group(3)

    return aliases

def apply_aliases(layers, aliases):
    """Applies aliases (dict) to layers ([FileLayer])."""

    for layer in layers:
        for r, row in enumerate(layer.rows):
            for c, cell in enumerate(row):
                for alias in aliases.iterkeys():
                    if cell == alias: # alias match
                        layer.rows[r][c] = aliases[alias]
    return layers

