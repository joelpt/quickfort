import re
import os.path
from itertools import dropwhile
import csv
import zipfile
from xml2obj import xml2obj

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
    elif ext == '.xls':
        lines = read_xls_file(filename)
    elif ext == '.xlsx':
        lines = read_xlsx_file(filename)
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
        print cells
        # remove trailing empty cells
        while cells[-1] == '':
            print cells
            cells = cells[:-1]

        # test for multilayer separator #> or #<
        c = cells[0]
        m = re.match(r'\#(\>+|\<+)', c)
        if m:
            newlayer = FileLayer([m.group(1)], csv)
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
    """
    Read contents of first sheet in Excel 95-2003 (.xls) workbook file.
    """
    wb = xlrd.open_workbook(filename)
    sh = wb.sheet_by_index(0)

    lines = []
    for rownum in range(sh.nrows):
        lines.append(sh.row_values(rownum))

    return lines

def read_xlsx_file(filename):
    """
    Read contents of first sheet in Excel 2007 (.xlsx) workbook file.
    These .xlsx files are actually zip files containing xml files.
    """

    # get first sheet's rows
    zf = zipfile.ZipFile(filename)
    sheetdata = zf.read('xl/worksheets/sheet1.xml')
    xml = xml2obj(sheetdata)
    rows = xml.sheetData.row

    # get shared strings xml
    stringdata = zf.read('xl/sharedStrings.xml')
    xml = xml2obj(stringdata)
    strings = xml.si

    # extract cell values into lines; cell values are given
    # as ordinal index references into sharedStrings.xml:ssi.si
    # elements, whose actual value is found in node.t
    # @@@ TODO raise an error when c.v=='d' and not an int; that means
    # it is a formula and we don't do those. give back a useful error
    # by catching all errors in main() and output to stderr Error: ...

    # TODO account for blank lines which are missing from xml too...
    # time to split colcode up and use both parts

    lines = []
    for row in rows:
        cells = row.c
        line = []
        lastcol = 0
        for c in cells:
            # get column number
            colcode = re.match('^([A-Z]+)', str(c.r)).group(1)
            col = colcode_to_colnum(colcode)

            if col > lastcol + 1:
                # add interleaving blank cells (these are omitted
                # as xml elements so must be interpolated)
                line.extend([''] * (col - lastcol - 1))

            lastcol = col
            # add cell value looked-up from shared strings
            line.append(str(strings[int(c.v)].t))
        lines.append(line)

    return lines


def colcode_to_colnum(colcode):
    """Convert Excel style column ids, e.g. A, XFD, etc. to a column number."""
    if len(colcode) == 0:
        return 0
    return (ord(colcode[-1]) - ord('A') + 1) + \
        (26 * colcode_to_colnum(colcode[:-1]))
