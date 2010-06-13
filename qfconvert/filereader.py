"""Blueprint file reading/parsing operations."""

import re
import os.path
import zipfile
from xml2obj import xml2obj

import xlrd

from geometry import Point, Grid, GridLayer


class FileLayer:
    """
    Represents the rows/cells of a single layer within a blueprint/sheet.
    Includes an onexit member which specifies what keycodes should be used
    to transition from one FileLayer to the next (in a list of FileLayers).
    """

    def __init__(self, onexit, rows=None):
        self.onexit = onexit
        self.rows = rows or []

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

        # Make all rows the same width
        for row in self.rows:
            if len(row) < maxwidth:
                row.extend( [''] * (maxwidth - len(row)) )

        return

    def width(self):
        """Returns current width of FileLayer rows."""
        return len(self.rows[0]) if self.rows else 0

    def height(self):
        """Returns current height of FileLayer's rows (row count)."""
        return len(self.rows) if self.rows else 0

    @staticmethod
    def str_rows(layer, colsep = ''):
        """Returns a pretty-formatted string showing the layer's rows."""
        rowstrings = [colsep.join(['.' if c == '' else c[0] for c in row]) + \
            '|' for row in layer.rows]
        return '\n'.join(rowstrings)

    @staticmethod
    def str_layers(file_layers):
        """Returns a pretty-formatted string of the given file_layers."""
        s = ''
        for layer in file_layers:
            s += (FileLayer.str_rows(layer) + '\n') + \
                (''.join(['On Exit: '] + layer.onexit) + '\n')
        return s


def FileLayers_to_GridLayers(file_layers):
    """Convert a list of FileLayers to a list of GridLayers."""
    layers = []
    for fl in file_layers:
        # fill a new Grid
        grid = Grid()
        (x, y) = (0, 0)
        for row in fl.rows:
            # print row
            x = 0
            for cell in row:
                cell = cell.strip()
                if (cell == '#'):
                    # forced end of row
                    break
                else:
                    # Blank out marking (non-sent) chars
                    if cell in ('~', '`'):
                        cell = ''

                    # add this csv cell to the grid
                    grid.add_cell(Point(x, y), cell)
                    x += 1 # for next column
            y += 1 # for next line
        layers.append(GridLayer(fl.onexit, grid))
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
    other bits of information. CSV files are considered a single sheet.
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

    # break into the lines we want
    (top_line, lines) = (','.join(lines[0]), lines[1:])

    # remove trailing commas from top_line
    top_line = re.sub(r',+$', '', top_line)

    # extract build type, start() command if any, and comment if any
    m = re.match(r'^#(build|dig|query|place)\w*( +start\(.+?\))?( .+)?$',
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

    # break up csv into layers of cells, each separated by #> or #<
    filelayers = []
    csv = []
    for cells in lines:
        # whitespace-strip and de-unicode the cells
        cells = [str(c.strip()) for c in cells]

        # remove trailing empty and # cells
        # while cells and cells[-1] in ('', '#'):
        #     cells = cells[:-1]

        # test for multilayer separator #> or #<
        c = cells[0] if cells else ''
        m = re.match(r'\#(\>+|\<+)', c)
        if m:
            newlayer = FileLayer([m.group(1)], csv)
            filelayers.append(newlayer)
            csv = []
        else:
            csv.append(cells)

    if len(csv) > 0:
        filelayers.append( FileLayer( [], csv ) )

    for fl in filelayers:
        fl.fixup()

    return filelayers, build_type, start, start_comment, comment


def read_csv_file(filename):
    """
    Read contents of a .csv file.
    Returns a 2d list of cell values.
    """

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


def read_xls_file(filename, sheetid):
    """
    Read contents of first sheet in Excel 95-2003 (.xls) workbook file.
    Returns a 2d list of cell values.
    """

    wb = xlrd.open_workbook(filename)
    sh = wb.sheet_by_index(sheetid or 0)

    lines = []
    for rownum in range(sh.nrows):
        lines.append(sh.row_values(rownum))

    return lines


def read_xlsx_file(filename, sheetid):
    """
    Read contents of specified sheet in Excel 2007 (.xlsx) workbook file.
    .xlsx files are actually zip files containing xml files.

    Returns a 2d list of cell values.
    """

    if sheetid is None:
        sheetid = 1
    else:
        sheetid += 1 # sheets are numbered starting from 1 in xlsx files

    try:
        zf = zipfile.ZipFile(filename)
        sheetdata = zf.read('xl/worksheets/sheet%s.xml' % sheetid)
        xml = xml2obj(sheetdata)
        rows = xml.sheetData.row
    except:
        raise Exception, "Could not read xlsx file %s, worksheet id %s" % (
            filename, sheetid-1)


    # get shared strings xml
    stringdata = zf.read('xl/sharedStrings.xml')
    xml = xml2obj(stringdata)
    strings = xml.si

    # extract cell values into lines; cell values are given
    # as ordinal index references into sharedStrings.xml:ssi.si
    # elements, whose string-value is found in the node's t element
    lines = []
    lastrownum = 0
    for row in rows:
        rownum = int(row.r)
        if rownum > lastrownum + 1: # interpolate missing rows
            lines.extend([[]] * (rownum - lastrownum - 1))
        lastrownum = rownum
        cells = row.c

        line = []
        lastcolnum = 0
        for c in cells:
            # get column number
            colcode = re.match('^([A-Z]+)', str(c.r)).group(1)
            colnum = colcode_to_colnum(colcode)

            if colnum > lastcolnum + 1: # interpolate missing columns
                line.extend([''] * (colnum - lastcolnum - 1))

            lastcolnum = colnum
            # add cell value looked-up from shared strings
            line.append(str(
                '' if c.v is None or c.v == 'd' else strings[int(c.v)].t
                ))
        lines.append(line)
    return lines


def read_xls_sheets(filename):
    """Get a list of sheets and their ids from xls file."""

    wb = xlrd.open_workbook(filename)
    return [(name, i) for i, name in enumerate(wb.sheet_names())]

def read_xlsx_sheets(filename):
    """Get a list of sheets and their ids from xlsx file."""
    try:
        zf = zipfile.ZipFile(filename)
        sheetsdata = zf.read('xl/workbook.xml')
        xml = xml2obj(sheetsdata)
        sheets = xml.sheets.sheet
    except:
        raise Exception, "Could not open '%s' for sheet listing." % filename

    output = []
    for sheet in sheets:
        m = re.match('rId(\d+)', sheet.r_id)
        if not m:
            raise Exception, "Could not read list of xlsx's worksheets."
        output.append( ( sheet.name, int(m.group(1)) - 1 ) )
    return output


def colcode_to_colnum(colcode):
    """Convert Excel style column ids (A, BB, XFD, ...) to a column number."""
    if len(colcode) == 0:
        return 0
    else:
        return (ord(colcode[-1]) - ord('A') + 1) + \
            (26 * colcode_to_colnum(colcode[:-1]))
