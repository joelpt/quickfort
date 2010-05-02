import re
from grid_geometry import *

def parse_csv_file(filename):
    # read file contents
    f = open(filename)
    lines = f.readlines()
    lines = [line.strip() for line in lines]

    # remove all quotes
    lines = [line.replace('\"', '') for line in lines]

    # break into the lines we want
    (top_line, lines) = (lines[0], lines[1:])

    # remove trailing commas from top_line
    top_line = re.sub(r',+$', '', top_line)

    # extract build type, start() command if any, and comment if any
    m = re.match(r'^#(\w+)( +start\(.+?\))?( .+)?$', top_line)
    (build_type, start_command, comment) = m.group(1, 2, 3)

    # break down start_command if given
    # expected format: start(x;y;start_comment)
    if start_command is not None:
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

    # fill in a new Grid
    grid = Grid()

    (x, y) = (0, 0)
    for line in lines:
        x = 0
        # print len(line.split(','))
        for cell in line.split(','):
            cell = cell.strip()
            if (cell == '#'):
                # end of a line
                break
            else:
                # Blank out marking (non-sent) chars
                if cell in ('~', '`'): cell = ''

                # print "want to add " + str(Point(x, y)) + cell
                # add this csv cell to the grid
                grid.add_cell(Point(x, y), cell)
                x += 1 # for next column
        y += 1 # for next line

    return (grid, build_type, start_pos, start_comment, comment)
