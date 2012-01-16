"""Reading and parsing .xlsx format blueprints."""

import re
import zipfile

from xml2obj import xml2obj

from errors import FileError


def read_xlsx_file(filename, sheetid):
    """
    Read contents of specified sheet in Excel 2007 (.xlsx) workbook file.
    .xlsx files are actually zip files containing xml files.

    Returns a 2d list of cell values.
    """

    if sheetid is None:
        sheetid = 1
    else:
        sheetid += 1  # sheets are numbered starting from 1 in xlsx files

    # Get cell data from specified worksheet.
    try:
        zf = zipfile.ZipFile(filename)
        sheetdata = zf.read('xl/worksheets/sheet%s.xml' % sheetid)
        xml = xml2obj(sheetdata)
        rows = xml.sheetData.row
    except:
        raise FileError("Could not read xlsx file %s, worksheet id %s" % (
            filename, sheetid - 1))

    # Get shared strings xml. Cell values are given as ordinal index
    # references into sharedStrings.xml:ssi.si elements, whose string-value
    # is found in the node's .t element.
    try:
        stringdata = zf.read('xl/sharedStrings.xml')
        xml = xml2obj(stringdata)
        strings = xml.si
    except:
        raise FileError("Could not parse sharedStrings.xml of xlsx file")

    # Map strings to row values and return result
    return extract_xlsx_lines(rows, strings)


def extract_xlsx_lines(sheetrows, strings):
    """
    Extract cell values into lines; cell values are given as ordinal index
    references into sharedStrings.xml:ssi.si elements, whose string-value
    is found in the node's .t element.
    Returns 2d list of strings (cell values).
    """

    lines = []
    lastrownum = 0
    for row in sheetrows:
        rownum = int(row.r)
        if rownum > lastrownum + 1:  # interpolate missing rows
            lines.extend([[]] * (rownum - lastrownum - 1))
        lastrownum = rownum
        cells = row.c

        line = []
        lastcolnum = 0
        for c in cells:
            # get column number
            colcode = re.match('^([A-Z]+)', str(c.r)).group(1)
            colnum = colcode_to_colnum(colcode)

            if colnum > lastcolnum + 1:  # interpolate missing columns
                line.extend([''] * (colnum - lastcolnum - 1))

            lastcolnum = colnum
            # add cell value looked-up from shared strings
            line.append(str(
                '' if c.v is None or c.v == 'd' else strings[int(c.v)].t
                ))
        lines.append(line)
    return lines


def read_xlsx_sheet_names(filename):
    """Get a list of sheets and their ids from xlsx file."""
    try:
        zf = zipfile.ZipFile(filename)
        sheetsdata = zf.read('xl/workbook.xml')
        xml = xml2obj(sheetsdata)
        sheets = xml.sheets.sheet
    except:
        raise FileError("Could not open '%s' for sheet listing." % filename)

    output = []
    for sheet in sheets:
        m = re.match('rId(\d+)', sheet.r_id)
        if not m:
            raise FileError("Could not read list of xlsx's worksheets.")
        output.append((sheet.name, int(m.group(1)) - 1))
    return output


def colcode_to_colnum(colcode):
    """Convert Excel style column ids (A, BB, XFD, ...) to a column number."""
    if len(colcode) == 0:
        return 0
    else:
        return (ord(colcode[-1]) - ord('A') + 1) + \
            (26 * colcode_to_colnum(colcode[:-1]))
