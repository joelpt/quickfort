"""Read and parse .xls blueprints."""

import xlrd


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


def read_xls_sheet_names(filename):
    """Get a list of sheets and their ids from xls file."""

    wb = xlrd.open_workbook(filename)
    return [(name, i) for i, name in enumerate(wb.sheet_names())]
