"""Handles conversion from QF keycode lists to keystrokes or DF macros."""

from copy import copy
from math import sqrt
import os
import re
import random

from filereader import load_json
from geometry import Area, Direction, add_points, scale_point, midpoint
import exetest
import util

# load global KEY_LIST which is used liberally below and would be inefficient to constantly reload
KEY_LIST = load_json(os.path.join(exetest.get_main_dir(), "config/keys.json"))


class KeystrokerError(Exception):
    """Base class for keystroker errors."""


class Keystroker:
    """
    Computes keycodes needed to go through route and transforms those keycodes
    into keystrokes or DF macro commands.
    Returns list keystrokes or DF macro lines.
    """

    def __init__(self, grid, buildconfig):
        self.grid = grid
        self.buildconfig = buildconfig

    def plot(self, plots, cursor):
        """
        Follows the route given by plots, generating the keys necessary
        to plot/designate those areas in DF.

        Returns list of keycodes generated and ending cursor position
        as ([String], Point).
        """

        submenukeys = self.buildconfig.get('submenukeys')
        last_command = ''
        last_submenu = ''
        keys = copy(self.buildconfig.get('init')) or []
        completed = self.buildconfig.get('completed') or []

        # construct the list of keystrokes required to move to each
        # successive area and build it
        for pos in plots:
            cell = self.grid.get_cell(*pos)
            command = cell.command
            endpos = cell.area.opposite_corner(pos)
            subs = {}

            # get samecmd or diffcmd depending on if the command is
            # different from the previous iteration's command
            if command == last_command:
                nextcmd = self.buildconfig.get('samecmd', command) or []
            else:
                nextcmd = self.buildconfig.get('diffcmd', command) or []
                last_command = command

            # moveto = keys to move cursor to starting area-corner
            subs['moveto'] = self.move(cursor, pos)

            # setsize = keys to set area to desired dimensions
            setsizefun = getattr(self,
                self.buildconfig.get('setsize', command))
            setsize, newpos = setsizefun(pos, endpos)
            subs['setsize'] = setsize

            # look for mat selection syntax like Cw:1
            mat_label = None
            if ':' in command:
                match = re.search(r'(.+):([\w]+)$', command)
                if match is None:
                    raise KeystrokerError(
                        'Invalid characters in material label: ' + command)

                # split command:mat_label into command and mat_label
                command = match.group(1)
                mat_label = match.group(2)
                # TODO: pitch a fit if we're not in key output mode

            # subs['setmats'] keys are used to select mats for an area
            setmatscfg = self.buildconfig.get('setmats', command)
            if setmatscfg:
                setmatsfun = getattr(self, setmatscfg)
                subs['setmats'] = setmatsfun(cell.area.size(), mat_label)

            # handle submenus
            use_command = None
            for k in submenukeys:
                if re.match(k, command):
                    # this command needs to be called in a DF submenu
                    submenu = command[0]

                    if not last_submenu:
                        # entering a new submenu and not currently in one
                        subs['menu'] = submenu
                        subs['exitmenu'] = []
                        last_submenu = submenu
                    elif last_submenu != submenu:
                        # switching from one submenu to another
                        subs['exitmenu'] = ['^']  # exit previous submenu
                        subs['menu'] = submenu    # enter new menu
                        last_submenu = submenu
                    else:
                        # same submenu
                        subs['menu'] = []
                        subs['exitmenu'] = []

                    # drop the submenu key from command
                    use_command = command[1:]
                    continue

            # no known submenu found in command?
            if not use_command:
                if last_submenu:
                    # was in a submenu, now want to be at parent menu
                    subs['exitmenu'] = ['^']
                else:
                    # was at root menu and want to continue being there
                    subs['exitmenu'] = []

                subs['menu'] = []
                last_submenu = ''
                use_command = command[:]

            # break command into keycodes
            codes = split_keystring_into_keycodes(use_command)

            # substitute keycodes into nextcmd where we find the string 'cmd'
            nextcodes = []
            for c in nextcmd:
                if c == 'cmd':
                    nextcodes.extend(codes)
                else:
                    nextcmd.append(c)

            # nextcodes is now our command-key string
            subs['cmd'] = nextcodes

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

        # if we're in a submenu, exit it
        if last_submenu:
            keys.append('^')

        # append on-completed keys, if any
        keys.extend(completed)
        return (keys, cursor)

    @staticmethod
    def get_z_moves(zoffset):
        """ Get the apprioriate number of > or < chars reflecting zoffset. """
        if zoffset > 0:
            return ['>'] * zoffset
        if zoffset < 0:
            return ['<'] * abs(zoffset)
        return []

    def move(self, (x1, y1), (x2, y2), zoffset=0, allowjumps=True):
        """
        Returns list of keycodes needed to move DF cursor from (x1, y1)
        to (x2, y2) and adjust z-level by zoffset if provided.
        """

        keys = []

        # do z-moves first if needed
        keys += Keystroker.get_z_moves(zoffset)

        allow_overshoot = True  # whether we may overshoot the target coords
        while x1 != x2 or y1 != y2:  # while there are moves left to make..
            direction = Direction.get_direction((x1, y1), (x2, y2))

            # Get x and y component of distance between start and end
            dx = abs(x2 - x1)
            dy = abs(y2 - y1)

            if dx == 0:
                steps = dy  # moving on y axis only
            elif dy == 0:
                steps = dx  # moving on x axis only
            else:
                # determine max diagonal steps we can take
                # in this direction without going too far
                steps = min([dx, dy])

            keycode = ['[' + direction.compass + ']']
            jumpkeycode = ['[+' + direction.compass + ']']
            move = direction.delta()
            if not allowjumps or steps < 8 or not allow_overshoot:
                # render single movement keys
                keys.extend(keycode * steps)
                (x1, y1) = add_points((x1, y1), scale_point(move, steps))
                allow_overshoot = True
            else:
                # use DF's move-by-10-units commands
                jumps = (steps // 10)
                leftover = steps % 10
                jumpmove = scale_point(move, 10)

                # backtracking optimization
                if leftover >= 8:
                    # test if jumping an extra 10-unit step
                    # would put us outside of the bounds of
                    # the blueprint (want to prevent)
                    (xt, yt) = add_points((x1, y1), scale_point(jumpmove, (jumps + 1)))

                    if self.grid.is_out_of_bounds(xt, yt):
                        # just move there normally
                        keys.extend(keycode * leftover)
                        (x1, y1) = add_points((x1, y1), scale_point(move, steps))
                        # don't try to do this next iteration
                        allow_overshoot = False
                    else:
                        # permit overjump/backtracking movement
                        jumps += 1
                        (x1, y1) = add_points((x1, y1), scale_point(jumpmove, jumps))
                        allow_overshoot = True
                else:
                    # move the last few cells needed when using
                    # jumpmoves to land on the right spot
                    keys.extend(keycode * leftover)
                    # keys.append('%')
                    (x1, y1) = add_points((x1, y1), scale_point(move, steps))
                    allow_overshoot = True

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
        mid = midpoint(start, end)
        keys = self.move(start, mid)

        # resize construction
        area = Area(start, end)
        keys += ['{widen}'] * (area.width() - 1)
        keys += ['{heighten}'] * (area.height() - 1)

        return keys, mid

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
        mid = midpoint(start, end)
        keys = self.move(start, mid)

        return keys, mid

    def setmats_build(self, areasize, manual_label):
        """
        Returns keycodes needed to select materials for the given int areasize,
        and either generic material selection or manual(ly assisted)
        material selection.

        If manual_label is None, we prefix the "enter mats menu and wait"
        keycodes and postfix a "wait" to the keys needed to choose the mats.

        If manual_label is not None, we use {WaitAfterNext} and
        {SelectMat label count} keycodes for use by QFAHK for entering
        the material menu and doing manual material selection.
        """
        # generic mat selection
        if manual_label is None:
            keys = ['&', '%']  # {Enter}{Wait}
            if areasize == 1:
                keys += ['@']  # shift-enter
                return keys

            # Tries to avoid running out of a given material type by blithely
            # attempting to all-select from DF's materials list repeatedly.
            # qfconvert will attempt this 1+sqrt(areasize) times, which should
            # be good enough most of the time.
            reps = 1 if areasize == 1 else 1 + 2 * int(sqrt(areasize))
            keys += ['@', '{menudown}'] * (reps - 1)
            keys += ['%']  # {Wait} at the end

            return keys

        # Manually assisted material selection: enter materials menu and
        # wait for that region of the screen to change, then select manually
        # chosen material.
        return ['%>', '&',
            '{SelectMat %s %d}' % (manual_label, areasize)]

    def setmats_bridge(self, areasize, manual_label):
        """
        Returns keycodes needed to select materials for the given int areasize;
        see setmats_build() for basic description. This method differs
        from setmats_build() in how it determines how many mat units are needed
        to build bridges, which use a formula of (areasize//4)+1 instead.
        """
        return self.setmats_build(areasize / 4 + 1, manual_label)


def convert_keys(keys, mode, title):
    """
    Convert keycodes to desired output, based on mode.
    Returns string of all keystrokes or of DF macro-content.
    """

    transmode = 'macro' if mode == 'macro' else 'key'
    keys = translate_keycodes(keys, transmode)

    if mode == 'macro':
        return '\n'.join(convert_to_macro(keys, title)) + '\n'
    elif mode == 'key':
        return ''.join(keys)
    elif mode == 'keylist':
        return ','.join(keys)

    raise KeystrokerError('Unknown Keystroker.render() mode "%s"' % mode)


def translate_keycodes(keycodes, mode):
    """Translate keycodes based on given output mode."""
    return util.flatten([translate_keycode(k, mode) for k in keycodes])


def translate_keycode(keycode, mode):
    """
    Translate a given keycode against keylist and specified mode.
    Returns translation if one exists, or original keycode otherwise.
    """

    translated = KEY_LIST[mode].get(keycode.lower())

    if translated is None:
        return keycode  # no translation available, so pass it through as is

    return translated   # translation made


def convert_to_macro(keycodes, title):
    """Convert keycodes to DF macro syntax (complete macro file contents)."""
    keybinds = parse_interface_txt(
        os.path.join(exetest.get_main_dir(), 'config/interface.txt'))

    if not title:  # make up a macro title if one is not provided to us
        title = '~qf' + str(random.randrange(0, 999999999))

    output = [title]  # first line of macro is macro title

    for key in keycodes:
        if key == '':
            continue  # empty keycode, output nothing
        elif keybinds.get(key) is None:
            raise KeystrokerError(
                "Key '%s' not bound in config/interface.txt" % key)
        if key == '^':
            output.append('\t\tLEAVESCREEN')  # escape menu key
        else:
            output.extend(keybinds[key])
        output.append('\tEnd of group')
    output.append('End of macro')
    return output


def split_keystring_into_keycodes(keystring):
    """
    Breaks str into individual keycodes.
    Returns a list of keycode strings.
    """

    # prepare to break keystring into keycodes
    cmdedit = keystring
    # separate tokens with | chars...
    cmdedit = re.sub(r'\+\{Enter\}', '|@|', cmdedit)
    cmdedit = re.sub(r'\{', '|{', cmdedit)
    cmdedit = re.sub(r'\}', '}|', cmdedit)
    cmdedit = re.sub(r'\+\&', '|+&|', cmdedit)
    cmdedit = re.sub(r'\&', '|&|', cmdedit)
    cmdedit = re.sub(r'\^', '|^|', cmdedit)
    cmdedit = re.sub(r'\+(\w)', '|1:\\1|', cmdedit)
    cmdedit = re.sub(r'\!(\w)', '|4:\\1|', cmdedit)
    cmdedit = re.sub(r'\%wait\%', '|{wait}|', cmdedit)  # support QF1.x's %wait%
    cmdsplit = re.split(r'\|+', cmdedit)  # ...and split tokens at | chars.

    # break into individual keycodes
    codes = []
    for k in cmdsplit:
        if not k:
            continue

        if k[0] == '{':
            # check for keycodes like {Right 5}
            match = re.match(r'\{(\w+|[&^+%!]) (\d+)\}', k)
            if match is None:
                codes.append(k)  # preserve whole key-combos
            else:
                # repeat the specified keycode the specified number of times
                codes.extend(['{' + match.group(1) + '}'] * int(match.group(2)))
            continue

        if k[0:2] in ('1:', '4:'):
            codes.append(k)  # preserve Alt/Shift combos as distinct keycodes
            continue

        if k[0] in ('&', '^', '+', '%', '!'):
            codes.append(k)  # preserve these as distinct keycodes
            continue

        codes.extend(k)  # just separate a series of individual keystrokes

    return codes


def parse_interface_txt(path):
    """
    Parse DF-syntax interface.txt.
    Returns a dictionary with keycodes as keys, whose values are lists of
    DF macro commands bound to each keycode in interface.txt.
    """
    with open(path) as f:
        data = f.read()

    data = util.convert_line_endings(data)
    groups = [re.split('\n', kb) for kb in re.split(r'\[BIND:', data)]

    keybinds = copy(KEY_LIST)
    for kb in groups:
        if kb == ['']:
            continue

        bind = re.sub(r'(\w+):.+', r'\1', kb[0])
        keys = [re.sub(r'\[(KEY:|SYM:)(.+?)\]', r'\2', k) for k in kb[1:]]

        for k in keys:
            if k == '':
                continue
            if keybinds.get(k) is None:
                keybinds[k] = []
            keybinds[k].append('\t\t' + bind)
    return keybinds
