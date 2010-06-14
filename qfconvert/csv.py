"""Reading and parsing csv blueprints."""

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
