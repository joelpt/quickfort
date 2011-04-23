"""Blueprint file reading/parsing operations."""

import json
import re
import os.path
import csv

from xls import read_xls_file, read_xls_sheets
from xlsx import read_xlsx_file, read_xlsx_sheets

from geometry import Point
from grid import Grid, GridLayer
from util import Struct


def read_csv_file(filename):
    """
    Reads a CSV document at filename, strips the cells of leading/trailing
    whitespace, and returns [['a', 'b', ...], ...]
    """
    with open(filename) as f:
        return [[cell.strip() for cell in line] for line in csv.reader(f)]

def load_json(filename):
    """Loads a JSON document at filename and returns the decoded result."""
    with open(filename) as f:
        return json.load(f)

class FileLayer:
    """
    Represents the rows/cells of a single layer within a blueprint/sheet.
    Includes an onexit member which specifies what keycodes should be used
    to transition from one FileLayer to the next (in a list of FileLayers).
    """

    def __init__(self, onexit, rows=None):
        self.onexit = onexit
        self.rows = rows or []

    def width(self):
        """Returns current width of FileLayer rows."""
        return len(self.rows[0]) if self.rows else 0

    def height(self):
        """Returns current height of FileLayer's rows (row count)."""
        return len(self.rows) if self.rows else 0

    def cleanup(self):
        """Remove non-sending characters from cells."""
        self.rows = [['' if c in ('~', '`', '#') else c for c in r]
            for r in self.rows]

    def fixup(self):
        """
        Trim off extra cells to right of # symbols and make sure every row
        is of the same length.
        """
        maxwidth = 0

        # Find max width and trim off unwanted crap
        for i, cells in enumerate(self.rows):
            try:
                endat = cells.index('#') # find first # (row ender) in any
                if endat == 0:
                    raise Exception, "Blueprint has '#' in unexpected cell."
                else:
                    # trim off stuff from the found # to the right
                    cells = cells[0:endat]
            except:
                # trim off empty cells at end of row
                while cells and cells[-1] == '':
                    cells = cells[:-1]
                endat = len(cells)
            self.rows[i] = cells

            # update maxwidth
            maxwidth = max(maxwidth, endat)

        if maxwidth == 0:
            raise Exception, "Blueprint appears to be empty or zero-width."

        # Conform all rows to the same width
        for row in self.rows:
            if len(row) < maxwidth:
                row.extend( ['' for x in range(maxwidth - len(row))] )

        return

    @staticmethod
    def str_rows(rows, colsep = ''):
        """Returns a pretty-formatted string showing the given rows."""
        rowstrings = [colsep.join(['.' if c == '' else c[0] for c in row]) + \
            '|' for row in rows]
        return '\n'.join(rowstrings)

    @staticmethod
    def str_layers(file_layers):
        """Returns a pretty-formatted string of the given file_layers."""
        s = ''
        for layer in file_layers:
            s += (FileLayer.str_rows(layer.rows) + '\n') + \
                (''.join(['On Exit: '] + layer.onexit) + '\n')
        return s


def FileLayers_to_GridLayers(file_layers):
    """Convert a list of FileLayers to a list of GridLayers."""
    layers = []
    for fl in file_layers:
        layers.append(GridLayer(fl.onexit, Grid(fl.rows)))
    return layers


def get_sheets(filename):
    """
    Return list of sheets in file specified. For csv, just returns
    the csv as the only sheet.
    """
    ext = os.path.splitext(filename)[1].lower()
    name = os.path.basename(filename)
    if ext == '.csv':
        return [(name, 0)]
    elif ext == '.xls':
        return read_xls_sheets(filename)
    elif ext == '.xlsx':
        return read_xlsx_sheets(filename)
    else:
        raise NameError


def parse_file(filename, sheetid):
    """
    Parse the specified file/sheet into FileLayers and associated
    other bits of information.
    """

    # read lines in
    lines = read_sheet(filename, sheetid)

    # break into the lines we want
    (top_line, lines) = (','.join(lines[0]), lines[1:])

    # parse top line details
    details = parse_sheet_details(top_line)

    # break up lines into z-layers separated by #> or #<
    filelayers = split_zlayers(lines)

    # tidy up the layers
    for fl in filelayers:
        fl.fixup()
        fl.cleanup()

    return filelayers, details


def read_sheet(filename, sheetid):
    """
    Read ths specified sheet from the specified file.
    CSV files are considered a single sheet.
    """

    # verify file exists
    if not os.path.isfile(filename):
        raise Exception, 'File not found "%s"' % filename

    # read contents of the file into lines
    ext = os.path.splitext(filename)[1].lower()
    if ext == '.csv':
        lines = read_csv_file(filename)
    elif ext == '.xls':
        lines = read_xls_file(filename, sheetid)
    elif ext == '.xlsx':
        lines = read_xlsx_file(filename, sheetid)
    else:
        raise Exception, "Invalid file type '%s' (csv, xls, xlsx accepted)" \
            % ext

    # if there's a line that starts with #, treat it as the last line of
    # the blueprint and trim off everything from there to the end of lines
    for i, line in enumerate(lines):
        if line and line[0] == '#':
            lines = lines[0:i]

    return lines

class SheetDetails(Struct):
    """ Struct to store top line details returned from parse_sheet_details(). """
    build_type = None
    start = None
    start_comment = None
    comment = None

def parse_sheet_details(top_line):
    """
    Parses out build type, start pos/comment, and general comment
    from top line of blueprint. Returns an object with keyword
    properties .build_type, .start, .start_comment, .comment
    """
    # remove trailing commas from top_line
    top_line = re.sub(r',+$', '', top_line)

    # extract build type, start() command if any, and comment if any
    m = re.match(r'^#(build|dig|query|place)( +start\(.+?\))?( .+)?$',
        top_line)

    (build_type, start_command, comment) = m.group(1, 2, 3)

    build_type = build_type.lower()

    # break down start_command if given
    # expected format: start(x;y;start_comment)
    if start_command:
        m = re.match(r" +start\( *(\d+) *; *(\d+) *;? *(.+)? *\)",
            start_command)

        (start, start_comment) = (
            Point(int(m.group(1)) - 1, int(m.group(2)) - 1),
            m.group(3)
            )
    else:
        start = Point(0, 0)
        start_comment = ''

    # clean up comment
    if comment:
        comment = comment.strip()
        comment = re.sub(r',+$', '', comment)
        comment = re.sub(r',{2,}', '', comment)
    else:
        comment = ''

    return SheetDetails(build_type=build_type, start=start,
        start_comment=start_comment, comment=comment)


def split_zlayers(lines):
    """Break up lines into z-layer subsets, separated by #> or #<"""
    filelayers = []
    zlayer = []
    for cells in lines:
        # whitespace-strip and de-unicode the cells
        cells = [str(c.strip()) for c in cells]

        # test for multilayer separator #> or #<
        c = cells[0] if cells else ''
        m = re.match(r'\#(\>+|\<+)', c)
        if m:
            newlayer = FileLayer([m.group(1)], zlayer)
            filelayers.append(newlayer)
            zlayer = []
        else:
            zlayer.append(cells)

    if len(zlayer) > 0:
        filelayers.append( FileLayer( [], zlayer ) )

    return filelayers

