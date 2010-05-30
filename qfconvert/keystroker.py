import os
import re
import random

from geometry import *
import exetest
import util


KEY_LIST = {
    'key': {
        '[n]': '8',
        '[ne]': '9',
        '[e]': '6',
        '[se]': '3',
        '[s]': '2',
        '[sw]': '1',
        '[w]': '4',
        '[nw]': '7',
        '[+n]': '+8',
        '[+ne]': '+9',
        '[+e]': '+6',
        '[+se]': '+3',
        '[+s]': '+2',
        '[+sw]': '+1',
        '[+w]': '+4',
        '[+nw]': '+7',
        '[widen]': 'k',
        '[heighten]': 'u',
        '[menudown]': '{NumpadAdd}',
        '!': '{Enter}',
        '#': '+{Enter}',
        '%': '%wait%',
        '^': '{Esc}'
        },
    'macro': {
        '[n]': '0:8',
        '[ne]': '0:9',
        '[e]': '0:6',
        '[se]': '0:3',
        '[s]': '0:2',
        '[sw]': '0:1',
        '[w]': '0:4',
        '[nw]': '0:7',
        '[+n]': '1:8',
        '[+ne]': '1:9',
        '[+e]': '1:6',
        '[+se]': '1:3',
        '[+s]': '1:2',
        '[+sw]': '1:1',
        '[+w]': '1:4',
        '[+nw]': '1:7',
        '[widen]': 'k',
        '[heighten]': 'u',
        '[menudown]': '+',
        '!': '0:Enter',
        '#': '1:Enter',
        '%': ''
    }
}


class Keystroker:

    def __init__(self, grid, buildconfig):
        self.grid = grid
        self.buildconfig = buildconfig
        self.current_menu = None

    def plot(self, plots, cursor):
        submenukeys = self.buildconfig.get('submenukeys')
        last_command = ''
        last_submenu = ''
        keys = self.buildconfig.get('init') or []
        # construct the list of keystrokes required to move to each
        # successive area and build it
        for pos in plots:
            cell = self.grid.get_cell(pos)
            command = cell.command
            endpos = cell.area.opposite_corner(pos)
            subs = {}

            # only want to send (nonmenu) key command when we
            # need to switch modes for dig, but for build
            # we have to press the command key every time
            # new config vars 'samecmd', 'diffcmd'
            #  for 'd': [], ['cmd']
            #  for 'b': ['cmd'], ['cmd']
            # so when processing the 'cmd' replacement, get
            # one of these from cfg, and replace into that
            # .. plus submenu in/out logic, where if we change
            #    submenus (indeed if the last_command does not
            #    exactly match command), reset last_command to ''

            # get samecmd or diffcmd depending
            if command == last_command:
                nextcmd = self.buildconfig.get('samecmd', command) or []
            else:
                nextcmd = self.buildconfig.get('diffcmd', command) or []
                last_command = command
            # moveto = keys to move cursor to starting area-corner
            subs['moveto'] = self.move(cursor, pos)

            # setsize = keys to set area to desired dimensions
            setsizefun = self.buildconfig.get('setsize', command)
            setsize, newpos = setsizefun(self, pos, endpos)
            subs['setsize'] = setsize

            # setmats - keys to select mats for an area
            setmatsfun = self.buildconfig.get('setmats', command)
            if setmatsfun:
                subs['setmats'] = self.setmats(cell.area.size())

            # submenu?
            justcommand = None
            for k in submenukeys:
                if re.match(k, command):
                    submenu = command[0]

                    # entering a submenu from not being in one?
                    if not last_submenu:
                        subs['menu'] = submenu
                        subs['exitmenu'] = []
                        last_submenu = submenu
                    elif last_submenu != submenu:
                        # exit previous submenu
                        subs['exitmenu'] = ['^']
                        # enter new menu
                        subs['menu'] = submenu
                        last_submenu = submenu
                    else:
                        subs['menu'] = []
                        subs['exitmenu'] = []

                    # drop the submenu key from command
                    justcommand = command[1:]
                    continue
            if not justcommand:
                if last_submenu:
                    subs['exitmenu'] = ['^']
                else:
                    subs['exitmenu'] = []
                subs['menu'] = []
                last_submenu = ''
                justcommand = command[:]

            # break command into keys
            cmdedit = re.sub(r'\{', '|{', justcommand)
            cmdedit = re.sub(r'\}', '}|', cmdedit)
            cmdedit = re.sub(r'\+\!', '|+!|', cmdedit)
            cmdedit = re.sub(r'\!', '|!|', cmdedit)
            cmdedit = re.sub(r'\^', '|^|', cmdedit)
            cmdsplit = re.split(r'\|+', cmdedit)

            cmdkeys = []
            for k in cmdsplit:
                if k[0] in ('{', '!', '^', '+'):
                    cmdkeys.append(k) # preserve whole key-combos
                else:
                    cmdkeys.extend(k) # separate individual keystrokes

            # substitute cmdkeys into nextcmd
            nextcmdkeys = []
            for c in nextcmd:
                if c == 'cmd':
                    nextcmdkeys.extend(cmdkeys)
                else:
                    nextcmd.append(c)

            # nextcmdkeys is now our command-key string
            subs['cmd'] = nextcmdkeys

            pattern = self.buildconfig.get('designate', command)

            newkeys = []
            # do pattern subs (and throw away empty elements)
            for p in pattern:
                if p in subs:
                    newkeys.extend(subs[p])
                else:
                    newkeys.append(p)

            # add our transformed keys to keys
            keys.extend(newkeys)

            # move cursor pos to end corner of built area
            cursor = newpos
        return keys

    def move(self, start, end):
        keys = []
        allow_backtrack = True

        # while there are moves left to make..
        while (start != end):
            direction = Direction.get_direction(start, end)

            # Get x and y component of distance between start and end
            dx = abs(start.x - end.x)
            dy = abs(start.y - end.y)

            if dx == 0:
                steps = dy # moving on y axis only
            elif dy == 0:
                steps = dx # moving on x axis only
            else:
                # determine max diagonal steps we can take
                # in this direction without going too far
                steps = min([dx, dy])

            keycode = ['[' + direction.compass + ']']
            jumpkeycode = ['[+' + direction.compass + ']']
            move = direction.delta()
            if steps < 8 or not allow_backtrack:
                # render keystrokes
                keys.extend(keycode * steps)
                start = start + (move * steps)
                allow_backtrack = True
            else:
                jumps = (steps // 10)
                leftover = steps % 10
                jumpmove = move * 10

                # backtracking optimization
                if leftover >= 8:
                    # test if jumping an extra 10-unit step
                    # would put us outside of the bounds of
                    # the blueprint (want to prevent)
                    test = start + (jumpmove * (jumps + 1))

                    if self.grid.is_out_of_bounds(test):
                        # just move there normally
                        keys.extend(keycode * leftover)
                        start = start + (move * steps)
                        # don't try to do this next iteration
                        allow_backtrack = False
                    else:
                        # permit overjump/backtracking movement
                        jumps +=1
                        start = start + (jumpmove * jumps)
                        allow_backtrack = True
                else:
                    # move the last few cells needed when using
                    # jumpmoves to land on the right spot
                    keys.extend(keycode * leftover)
                    # keys.append('%')
                    start = start + (move * steps)
                    allow_backtrack = True

                if jumps > 0:
                    keys.extend(jumpkeycode * jumps)

        return keys

    def setsize_standard(self, start, end):
        """
        Standard sizing mechanism for dig, place, query buildtypes.
        Returns keys, newpos:
            keys needed to make the currently-designating area the correct size
            pos is where the cursor ends up after sizing the area
        """
        return self.move(start, end), end

    def setsize_build(self, start, end):
        """
        Standard sizing mechanism for the build buildtype.
        Returns keys, pos:
            keys needed to make the currently-designating area the correct size
            pos is where the cursor ends up after sizing the area
        """
        # move cursor halfway to end from start
        midpoint = start.midpoint(end)
        keys = self.move(start, midpoint)

        # resize construction
        area = Area(start, end)
        keys += ['[widen]'] * (area.width() - 1)
        keys += ['[heighten]'] * (area.height() - 1)

        return keys, midpoint

    def setsize_fixed(self, start, end):
        """
        Sizing mechanism for fixed size buildings like 3x3 workshops,
        5x5 trade depots and 5x5 siege workshops. Here we just move to
        the center of the building and deploy it. This allows for e.g.
        a 3x3 grid of 'wc' cells indicating a single carpenter's workshop.
        Returns keys, pos:
            keys needed to make the currently-designating area the correct size
            pos is where the cursor ends up after sizing the area
        """
        # move cursor halfway to end from start
        midpoint = start.midpoint(end)
        keys = self.move(start, midpoint)

        return keys, midpoint

    def setmats(self, areasize):
        """
        Tries to avoid running out of a given material type by blithely
        attempting to all-select from DF's materials list repeatedly.
        qfconvert will attempt this 1+sqrt(areasize) times, which should
        be good enough most of the time.
        """
        if areasize == 1: return ['#']

        reps = 2 * int(sqrt(areasize))
        keys = ['#', '[menudown]'] * (reps - 1)
        keys.append('#')
        return keys



def convert_keys(keys, mode, title):
    keys = translate_keystrokes(keys, mode)
    if mode == 'macro':
        return '\n'.join(convert_to_macro(keys, title)) + '\n'
    elif mode == 'key':
        return ''.join(keys)
    else:
        raise Exception, 'Unknown Keystroker.render() mode "%s"' % mode


def translate_keystrokes(keys, mode):
    return util.flatten( [ translate_keystroke(k, mode) for k in keys ] )


def translate_keystroke(key, mode):
    return KEY_LIST[mode].get(key) or key


def convert_to_macro(keys, title):
    keybinds = parse_interface_txt(
        os.path.join(exetest.get_main_dir(), 'interface.txt') )

    if not title:
        title = '@@@qf' + str(random.randrange(0, 999999999))

    output = [title] # first line of macro is macro title

    for key in keys:
        if keybinds.get(key) is None:
            raise Exception, \
                "Key '%s' not bound in interface.txt" % key
        if key == '^':
            output.append('\t\tLEAVESCREEN') # escape menu key
        else:
            output.extend(keybinds[key])
        output.append('\tEnd of group')
    output.append('End of macro')

    return output


def parse_interface_txt(path):
    with open(path) as f:
        data = f.read()

    groups = [re.split('\n', kb) for kb in re.split(r'\[BIND:', data)]

    keybinds = KEY_LIST
    for kb in groups:
        if kb == ['']:
            continue

        bind = re.sub(r'(\w+):.+', r'\1', kb[0])
        keys = [re.sub(r'\[(KEY:|SYM:)(.+?)\]', r'\2', k)
            for k in kb[1:] ]

        for k in keys:
            if k == '':
                continue
            if keybinds.get(k) is None:
                keybinds[k] = []
            keybinds[k].append('\t\t' + bind)
    return keybinds
