import re
import os.path
from itertools import dropwhile
import csv

import xlrd

from geometry import *

class FileLayer:

    def __init__(self, onexit, rows=None):
        self.onexit = onexit
        self.rows = rows or []

def parse_file(filename):
    layers = []

    # read contents of the file into lines
    ext = os.path.splitext(filename)[1].lower()
    if ext == '.csv':
        lines = read_csv_file(filename)
    elif ext in ('.xls', '.xlsx'):
        lines = read_xls_file(filename)
    else:
        raise NameError

    # break into the lines we want
    (top_line, lines) = (','.join(lines[0]), lines[1:])

    # remove trailing commas from top_line
    top_line = re.sub(r',+$', '', top_line)

    # extract build type, start() command if any, and comment if any

    m = re.match(r'^#(build|dig|query|place)\w*( +start\(.+?\))?( .+)?$', top_line)
    (build_type, start_command, comment) = m.group(1, 2, 3)
    build_type = build_type.lower()

    # break down start_command if given
    # expected format: start(x;y;start_comment)
    if start_command:
        m = re.match(r" +start\( *(\d+) *; *(\d+) *;? *(.+)? *\)",
            start_command)

        (start_pos, start_comment) = (Point(int(m.group(1)), int(m.group(2))),
            m.group(3))
    else:
        start_pos = None
        start_comment = None

    # clean up comment
    if comment:
        comment = comment.strip()
        comment = re.sub(r',+$', '', comment)
        comment = re.sub(r',{2,}', '', comment)
    else:
        comment = ''

    # break up csv into layers of cells, with each
    # layer separated by #> or #<

    csvlayers = []
    csv = []
    for cells in lines:
        # whitespace-strip and de-unicode the cells
        cells = [str(c.strip()) for c in cells]
        # print cells
        # remove trailing empty cells
        cells = list(dropwhile(lambda x: x == '', cells[::-1]))[::-1]

        # test for multilayer separator #> or #<
        c = cells[0]
        if c in ('#>', '#<'):
            newlayer = FileLayer(['^5' if c == "#>" else '+5'], csv)
            csvlayers.append(newlayer)
            csv = []
        else:
            csv.append(cells)

    if len(csv) > 0:
        csvlayers.append( FileLayer( [], csv ) )

    layers = []
    for csvlayer in csvlayers:
        # fill a new Grid
        grid = Grid()
        (x, y) = (0, 0)
        for row in csvlayer.rows:
            # print row
            x = 0
            for cell in row:
                cell = cell.strip()
                if (cell == '#'):
                    # end of a line
                    break
                else:
                    # Blank out marking (non-sent) chars
                    if cell in ('~', '`'): cell = ''

                    # add this csv cell to the grid
                    grid.add_cell(Point(x, y), cell)
                    x += 1 # for next column
            y += 1 # for next line
        grid.fixup()
        layers.append(GridLayer(csvlayer.onexit, grid))

    return (layers, build_type, start_pos, start_comment, comment)


def read_csv_file(filename):
    # read file contents
    with open(filename) as f:
        lines = f.readlines()

    # remove any leading or trailing whitespace
    lines = [line.strip() for line in lines]

    # remove all quotes
    lines = [line.replace('\"', '') for line in lines]

    # turn lines into lists of cells
    lines = [line.split(',') for line in lines]

    return lines


def read_xls_file(filename):
    # read contents of first sheel in excel workbook file
    wb = xlrd.open_workbook(filename)
    sh = wb.sheet_by_index(0)

    lines = []
    for rownum in range(sh.nrows):
        lines.append(sh.row_values(rownum))
    # print lines
    return lines