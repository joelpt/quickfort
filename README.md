Quickfort 2.04
===============
by joelpt <quickfort@joelpt.net>

<http://joelpt.net/quickfort>


User Manual
===========

Quickfort 2 is a utility for Dwarf Fortress that helps you build fortresses
from "blueprint" .CSV, .XLS, and .XLSX files. Many applications exist to edit
these files, such as MS Excel and Google Docs. Most building-oriented DF
commands are supported through the use of multiple files/worksheets, each
describing a different phase of DF construction (designation, building,
stockpiles, and making adjustments).

Original idea and 1.0 codebase from [Valdemar's designator.ahk script](http://www.bay12games.com/forum/index.php?topic=1428.0).

User contributed blueprints can be found [here](http://www.mediafire.com/?oujvalbb0sggp).

See the [Links section](#links) for various tools that work with Quickfort.


Table of Contents
-----------------

* [Features](#features)
* [For the impatient](#for-the-impatient)
* [Quickfort 2.0: What's new](#quickfort-20-whats-new)
* [For users of Quickfort 1.x](#for-users-of-quickfort-1x)
* [Windows Quick Start](#windows-quick-start)
* [Linux/OSX Quick Start](#linuxosx-quick-start)
* [Windows Basic Usage](#windows-basic-usage)
* [Editing Blueprints](#editing-blueprints)
  * [Area expansion syntax](#area-expansion-syntax)
  * [Automatic area expansion](#automatic-area-expansion)
  * [Specifying a starting position](#specifying-a-starting-position)
  * [Multilevel blueprints](#multilevel-blueprints)
  * [Multiple build phases](#multiple-build-phases)
  * [Manual material selection](#manual-material-selection)
  * [Minecart tracks](#minecart-tracks)
* [Command prompt](#command-prompt)
* [Transformations](#transformations)
  * [Transformations: Simple repetition](#transformations-simple-repetition)
  * [Transformations: Simple transformation](#transformations-simple-transformation)
  * [Advanced transformations](#advanced-transformations)
    * [Advanced transformations: alignment](#advanced-transformations-alignment)
    * [Advanced transformations: the whirlpool pattern](#advanced-transformations-the-whirlpool-pattern)
    * [Advanced transformations: multiple Z-levels](#advanced-transformations-multiple-z-levels)
    * [Advanced transformations: the ! command](#advanced-transformations-the--command)
    * [Advanced transformations: Search and replace](#advanced-transformations-search-and-replace)
    * [Advanced transformations: Change build phase](#advanced-transformations-change-build-phase)
    * [Advanced transformations: debugging](#advanced-transformations-debugging)
* [Stupid dwarf tricks](#stupid-dwarf-tricks)
* [Troubleshooting](#troubleshooting)
* [Create an Excel macro to size all columns to a uniform narrow width](#create-an-excel-macro-to-size-all-columns-to-a-uniform-narrow-width)
* [Other Excel tips](#other-excel-tips)
* [Links](#links)
* [Todo/Future Ideas](#todofuture-ideas)
* [Changelog](#changelog)
* [Credits and License](#credits-and-license)


Features
--------

* Design complete blueprints to handle 4 main phases of DF construction
* .CSV and multi-worksheet .XLS/.XLSX blueprint files supported
* Intelligent designator minimizes keystrokes needed to designate blueprints
* Designates fast: 10x faster than QF1.11 typical
* Manual material selection allows you to specify construction materials used
* Multi-Z-level blueprints
* Blueprint transformation (rotate, replace, repeat in up to 3 dimensions)
* Aliases to automate frequent keystroke combos
* Minimalist (and optional) GUI for Windows
* Simple "command line" entry mode in GUI
* Win/Linux/OSX support via command line qfconvert utility (Python based)
* DF macro- or keysending-based output methods supported
* Assortment of sample blueprints included


For the impatient
-----------------

WINDOWS USERS: Run Quickfort.exe for the GUI interface.

LINUX/OSX USERS: Please set `[MACRO_MS:0]` in your `data/init/init.txt`
for best DF macro playback performance.

Run the command line qfconvert tool via python to generate DF macro files:

    > cd src/qfconvert
    > python ./qfconvert.py

or `chmod +x qfconvert.py` to run it like a shell script.

Command line example using qfconvert:

    > python ./qfconvert.py myblueprint.xls <DF folder>/data/init/macros/foo.mak

... then play your macro in DF with Ctrl+L, select foo, Ctrl+P.


Quickfort 2.0: What's new
-------------------------

See the [changelog](#changelog) for newer changes since version 2.00.

Quickfort 2.0 is a major rewrite of Quickfort 1.11.

The new blueprint conversion engine 'qfconvert' has been rewritten in cross-
platform Python, enabling non-Windows users to utilize the app via the command
line. More importantly, the use of Python makes possible a much more advanced
implementation of how Quickfort does its job.

The new conversion engine is much smarter about how it designates your
blueprints. Instead of using the "typewriter" (line-by-line) approach of
QF1.x, QF2 tries to minimize the total number of commands (keystrokes) sent to
Dwarf Fortress. It does this by analyzing your blueprint, finding the largest
contiguous areas that can possibly be designated with single DF commands; for
example, a 10x10 room can be dug out with one 'd' command instead of 100
single-tile designations. While designating these areas, QF2 also attempts to
minimize the amount of cursor travel between areas.

QF2 is smarter about designating objects of various sizes. For example,
workshops can now be designated by filling a 3x3 area of a blueprint with 'wc'
instead of just a single 'wc' in the center of a 3x3 area. This makes some
kinds of blueprints easier to create and read.

The new engine also has a reworked blueprint transformation framework which
supports things like blueprint repetition, rotation, and in-cell modification.

QF2 supports outputting and executing DF macros instead of sending keystrokes
to the DF window  (QF1.x style). This results in blueprint playbacks that are
faster and more reliable vs. keysending. Since DF macros are native to DF,
they can be used on any OS that runs Dwarf Fortress. Keysending is still used
by the Windows-only Quickfort GUI for certain operations, i.e. Alt+V
"visualize".

Quickfort's minimalist Windows-only "GUI" is a partial rewrite of the
AutoHotKey script that was Quickfort 1.x. It has seen a number of significant
improvements, such as blueprint previews and the ability to choose a worksheet
from a multisheet XLS/XLSX file. It is now a "thin" GUI implementation,
providing only the mousetip-based GUI and DF-keysending functionality, and
relying on qfconvert for all blueprint processing and manipulation.

A list of the shiny new bits:

* Conversion engine rewritten in cross-platform Python
* Intelligent designator: ~25% as many DF commands required as QF1.x for the
  same tasks (no more "typewriter" style playback)
* DF macros support: faster, more reliable, works cross-platform
* XLS/XLSX (Excel) workbooks support makes it easy to bundle multi-phase
  blueprints
* Improved Windows GUI, including enhanced blueprint info/select GUI and
  shrinkable mousetip
* Alt-R repeat syntax expanded to support basic transformations,
  e.g. `fliph flipv 2e`
* Alt-T command line supports multi-row entry, e.g. `dig d,d#d,d`
* Multi-cell buildings can be plotted in multiple cells instead of from the
  'center' tile
* Build logic and keystroke/macro mappings configurable via config files

This new codebase for Quickfort 2.0 will enable lots of interesting new
features and experiments in future releases. Features such as '#all'
blueprints, '#meta' blueprints, and an Undo mode are all on the 2.x release
schedule.


For users of Quickfort 1.x
--------------------------

A few things have changed in Quickfort's basic operation in the move from 1.0 to
2.0:

* Alt+D no longer opens a blueprint file AND plays it. Instead, Alt+F is now
  used to open a file, and Alt+D is used to play the file. This enables Alt+D
  to work a bit like a "stamp" tool, but may be disconcerting to experienced
  QF1 users at first.

* QF2 now outputs DF macros by default. This is faster and more reliable than
  QF1's key-sending approach, though that approach is still supported; use Alt+K
  to toggle modes.

* Be sure to set `[MACRO_MS:0]` in your DF's `data/init/init.txt` or macro
  playback will be painfully slow.


Windows Quick Start
-------------------

1. Download and extract the Quickfort2.##.zip file from <https://github.com/joelpt/quickfort/downloads>
2. Run Quickfort.exe.
3. Launch Dwarf Fortress and get into a Fortress mode game.
4. Press Alt+F to open the Quickfort file browser.
5. Browse into the Tests folder and select `obama.csv`
6. Some information will be shown about the blueprint in a popup window. Click
   OK to continue.
7. Follow Quickfort's tooltip instructions to switch to Designate mode and
   select an empty underground z-level.
8. Press Alt+V to see the outline of where the blueprint will be placed. The
   entire area should be clear.
9. If you are satisfied (start at least 3 cells from the map edge), press Alt+D
   to designate.
10. Wait a few seconds while the blueprint is designated.


Linux/OSX Quick Start
---------------------

You must have Python 2.6.4 installed.

Run the command line conversion tool via python:

    > cd src/qfconvert
    > python ./qfconvert.py

or `chmod +x qfconvert.py` and run it like a shell script.

Examples:

    > python ./qfconvert.py --info myblueprint.xls
      (..information about myblueprint.xls..)

    > python ./qfconvert.py myblueprint.xls <DF folder>/data/init/macros/foo.mak

... then play mymacro.mak in DF with Ctrl+L, select foo, Ctrl+P.


Windows Basic Usage
-------------------

Please see the [Troubleshooting section](#troubleshooting) for solutions to
common problems.

Quickfort's GUI consists of a mouse tooltip, hotkeys and a few popup windows.

Start Dwarf Fortress (windowed mode recommended). Run Quickfort.exe.

Use Alt+F to select a CSV file to execute. There are some samples in the
Blueprints folder. Quickfort will give instructions in the mouse tooltip for
positioning the in-game cursor.

Once positioned, use Alt+D to begin designating your blueprint in game.
Quickfort will send the commands necessary to DF to dig, build, place, or
query according to the chosen blueprint.

Alt+Q/W/A/S can be used to change the starting corner for the blueprint (that
is, which corner of the blueprint you'll put the starting cursor at). The
current starting corner setting will be shown in the QF tooltip. These hotkeys
have no effect if the blueprint specifies a starting cursor position; see
the [Specifying a starting position section](#specifying-a-starting-position)
for more details.

Alt+R can be used to repeat a blueprint any number of times to the north, south,
east, west, up, and down. This can be useful for digging multilevel
staircases/shafts, repeating room complexes, etc. Alt+R can also be used to
rotate, flip, tesselate, and search-and-replace blueprints: see the
[Transformations section](#transformations) for more details.

Alt+T opens the Quickfort command line. Here you can enter a single-line
QF-style command. Commands entered this way can be repeated with Alt+R as well.

After a build completes, Alt+D can be used to designate the same blueprint
again, or use Alt+F again to select a new blueprint. Alt+E can be used to select
a different worksheet from a currently selected multisheet XLS/XLSX file, or
just view the information for the current CSV or worksheet.

Alt+N can be used to save a named macro to DF's macros folder. This can be
useful if you designate a particular blueprint often and would rather access
it from DF's Ctrl+L menu than go through Quickfort every time.

Alt+H can be used to hide QF's mouse tooltip; all hotkeys will continue to
work. Alt+M toggles from QF's rather wordy mousetip to a minimal one, if you
know what you're doing.

Alt+K toggles between macro and keys modes. In macro mode, QF will utilize
DF's built-in macro functionality to execute commands. In keys mode, QF will
literally send keystrokes to the DF window to perform those same commands
(this was QF1.x's approach). Keys mode is a bit slower, but if you're having
trouble designating with macro mode, try switching to keys mode.

Shift+Alt+Z suspends/resumes Quickfort, useful if you find it to interfere
with other windows.

Shift+Alt+X exits Quickfort.


Editing Blueprints
------------------

The format of Quickfort-compatible blueprint files is straightforward.

Use a spreadsheet editor such as Excel, Google Docs, or LibreOffice to edit
these files. There are also a number of blueprint editing tools that export
Quickfort compatible blueprint files; see the [Links section](#links).

The first line of the spreadsheet should look like this:

    #dig This is a comment.

The keyword "dig" tells Quickfort we are going to be using the Designations menu
in DF. The following build phase keywords are understood:

    dig     Designations menu (d)
    build   Build menu (b)
    place   Place stockpiles menu (p)
    query   Set building tasks/prefs menu (q)

Optionally following this keyword and a space, you may enter a comment. This
comment will appear by default after loading the blueprint with Quickfort
(Alt+F). You can use this space for explanations, attribution, etc. Newlines
may be embedded by using \n.

Below this line begin entering the keys you want sent in each cell. For
example, we could dig out a 4x4 room like so (spaces are used as column
separators here):

    #dig
    d d d d #
    d d d d #
    d d d d #
    d d d d #
    # # # # #

Note the # symbols at the right end of each row and below the last row. These
are completely optional, but can be helpful for layout purposes.

If you run into problems (e.g. Excel saving 'blank' cells and rows
unnecessarily), use `#` symbols as shown above to clearly delineate the area.
They tell QF where the edges of your blueprint are. They can also be used to
enforce a blueprint of a larger width or height than the filled cells would
otherwise occupy.

Once the dwarves have that dug out, let's build a walled in bedroom within our
dug-out area:

    #build
    Cw Cw Cw Cw #
    Cw b  h  Cw #
    Cw       Cw #
    Cw Cw d  Cw #
    #  #  #  #  #

Note my generosity - I've placed a bed (b), chest (h) and door (d) here as
well. Note that you must use the full series of keys needed to build something
in each cell, e.g. 'Cw' enters DF's constructions submenu (C) and selects
walls (w).

I'd also like to place a booze stockpile in the 2 unoccupied tiles in the room.

    #place Place a food stockpile
    ` ` ` ` #
    ` ` ` ` #
    ` f(2x1)#
    ` ` ` ` #
    # # # # #

This illustration may be a little hard to understand. The f(2x1) is in column 2,
row 3. All the other cells are empty. QF considers both ` and ~ characters
within cells to be empty cells; this can help with multilayer or fortresswide
blueprint layouts as 'chalk lines'.

With f(2x1), we've asked QF to place a Food stockpile 2 units wide by 1 high
unit, or f(2x1). QF sends the necessary keys to resize the placement region.
This also works properly in all modes, including build mode (floors Cf(10x10),
bridges ga(4x4), etc. that are sized with UMKH keys).

Note that the f(2x1) syntax isn't actually necessary here; we could have just
used:

    #place Place a food stockpile
    ` ` ` ` #
    ` ` ` ` #
    ` f f ` #
    ` ` ` ` #
    # # # # #

QF2 is smart enough to recognize this as a 2x1 food stockpile, and creates it
as such rather than as two 1x1 food stockpiles. This applies to most cases
where f(WxH) could also be used. The f(WxH) style can still be useful in cases
where the layout would be ambiguous; consider an L-shaped food stockpile(s).

Lastly, let's turn the bed into a bedroom, and set the food stockpile to hold
only booze.

    #query
    ` ` ` ` #
    ` r+` ` #
    ` booze #
    ` ` ` ` #
    # # # # #

In column 2, row 2 we have "r+". This sends r+ keys to DF when the cursor is
over the bed, causing us to 'make room' and then increase its size to ensure the
'room' fills the entire area.

In column 2, row 3 we have "booze". booze is an alias keyword defined in the
included config/aliases.txt file. This particular alias sets a food stockpile to
carry booze only, by sending the commands needed to navigate DF's stockpile
settings menu.

The included Blueprints/Examples/bedroom-*.csv files provide a good simple
example of a 4-layer QF blueprint. Check out aliases.txt for some helpful
starting aliases. Blueprints/TheQuickFortress/ provides a good detailed set of
examples covering some more complex designs.


Area expansion syntax
---------------------

In Quickfort 2.0, the following blueprints are equivalent:

    #dig a 3x3 area
    d d d #
    d d d #
    d d d #
    # # # #

    #dig the same area with d(3x3) specified in row 1, col 1
    d(3x3)#
    ` ` ` #
    ` ` ` #
    # # # #

The second example uses Quickfort's "area expansion syntax", which always
takes the form:

    cmds(WxH)

In Quickfort 2.0, the above two examples of specifying a contiguous 3x3 area
produce identical output: a single 3x3 designation will be performed, rather
than nine 1x1 designations as the first example might suggest.

Sometimes, how an area should be identified is ambiguous:

    #place L shaped food stockpile
    f f ` ` #
    f f ` ` #
    f f f f #
    f f f f #
    # # # # #

QF2 wants to make the largest contiguous areas. Should it draw a tall 2x4 food
stockpile on the left with a second 2x2 stockpile in the lower right? Or
should it have a long 4x2 along the bottom with a 2x2 in the upper left? QF2
will choose one or the other, but you have no guarantee which way it will
choose.

If you need to guarantee a certain area arrangement unambiguously, use area
expansion syntax:

    # place L shaped food stockpile; ~ markers denote placement (ignored by QF2)
    f(2x4)` #
    ~ ~ ` ` #
    ~ ~ f f #
    ~ ~ f f #
    # # # # #


Automatic area expansion
------------------------

In Quickfort 1.x, buildings larger than 1x1, like workshops, had to be placed
in blueprints in a single cell, usually in the "center" of the building's
footprint, with empty cells around it to leave room for that footprint.

Starting with Quickfort 2.0, this is no longer necessary.

The following blueprints are equivalent:

    #build workshop in row 2, col 2 that will occupy the 3x3 area (QF1.x style)
    `  `  `  #
    `  wm `  #
    `  `  `  #
    #  #  #  #

    #build workshop: QF2 understands that we want one 3x3 workshop
    wm wm wm #
    wm wm wm #
    wm wm wm #
    #  #  #  #

This is called automatic area expansion.

Both the area expansion syntax and automatic area expansion also work for
buildings which have an adjustable size, like bridges. The following
blueprints are equivalent:

    #build a 4x2 bridge from row 1, col 1
    ga(4x2)  `  #
    `  `  `  `  #
    #  #  #  #  #

    #build the same bridge
    ga ga ga ga #
    ga ga ga ga #
    #  #  #  #  #

This can be especially helpful for laying out structures like screw pump towers
and waterwheels, whose "center point" can be non-obvious.


Specifying a starting position
------------------------------

You can optionally specify a cursor starting position for a particular
blueprint, simplifying the task of blueprint alignment. This can be helpful
for blueprints that are based on a central staircase, for example.

To specify a cursor starting position, use the following modified format
for the header line of your blueprint:

    #mode start(X;Y;STARTCOMMENT) comment

where X and Y specify the starting cursor position (1;1 is the top left cell)
and STARTCOMMENT (optional) is a description displayed to the QF user of
where to position their cursor. This description appears in the pre-playback
mouse tooltip.

A couple examples:

    #dig start(3; 3; Center tile of a 5-tile square) Regular blueprint comment
    #build start(10;15)

When a start() parameter is found in a CSV file, the normal Alt+Q/W/A/S
keys will override (ignore) said parameter. Alt+Z will un-ignore the start()
parameter.

See Blueprints/Tests/starting-position.csv for a simple example.
The Blueprints/TheQuickFortress/*.csv examples all utilize start().


Multilevel blueprints
---------------------

Multilevel blueprints are accommodated by separating Z-levels of the blueprint
with #> (go down one z-level) or #< (go up one z-level) at the end of each
floor.

    #dig Stairs leading down to a small room below
    j  `  `  #
    `  `  `  #
    `  `  `  #
    #> #  #  #
    u  d  d  #
    d  d  d  #
    d  d  d  #
    #  #  #  #

Most multilevel blueprints use #>, but there are a few use cases for #< such
as building a screw pump tower. See Blueprints/Examples/screw-pump-tower-*.csv
for an example.


Multiple build phases
---------------------

A complete QF specification for a floor of your fortress may contain 4 or more
separate blueprints, one for each "phase" of construction (dig/designate,
build, place stockpiles, building adjustments).

Starting with Quickfort 2.0, all phases and even variations can be kept in a
single .XLS or .XLSX file using multiple worksheets. Tools like Excel make it
easy to work with multiple worksheets and also retains all worksheet styling
such as cell sizes and coloring.

After opening a multisheet XLS/XLSX blueprint using Alt+F, Quickfort will
present a dialog allowing you to choose which sheet to use. Alt+E can be
subsequently used to select a different sheet from the same file.

Quickfort 2.0 is also fully compatible with using single-sheet .CSV files for
blueprints. The build phases suggest a convenient naming scheme for CSV based
blueprint "stacks", as seen in the Blueprints/General folder:

    bedroom-dig.csv
    bedroom-build.csv
    bedroom-stockpile.csv
    bedroom-adjust.csv

The naming scheme is up to you, of course. A similar approach is used in the
Blueprints/TheQuickFortress folder.

Protip: After digging out an area, it's often wise to dump all leftover stone
in the area before beginning the build phase. You may also wish to smooth and/or
engrave the area before starting the build phase, as dwarves may be unable to
access walls/floors that are behind/under built objects.


Manual material selection
-------------------------

Quickfort supports manual material selection for #build blueprints. This enables
you to manually select the materials that Quickfort should build with during
playback.

Currently, manual material selection only works on Windows when using the
Quickfort GUI (Quickfort.exe). It also requires using QF's key-sending playback
method because user interaction is required during playback. Lastly, note that
this feature is considered EXPERIMENTAL. Most types of constructions should
work with manual material selection, but some are untested.

To use manual material selection, just append :label to the end of any cells
in a #build blueprint. `label` can be any alphanumeric label that you'd like
to use to identify the material to be used. Multiple different labels can be
used in a single blueprint, allowing for multiple distinct materials to be
applied during construction.

A simple example:

    #build Uses 3 different materials to build 3 rows of flooring
    Cf:top,Cf:top,Cf:top,Cf:top,Cf:top
    Cf:mid,Cf:mid,Cf:mid,Cf:mid,Cf:mid
    Cf:bot,Cf:bot,Cf:bot,Cf:bot,Cf:bot

After starting playback with Alt+D, when Quickfort first encounters a new
`:label`, you will be prompted to help Quickfort memorize the material you want
to use for cells with that label. There are three steps to memorize a material:

1. Use DF's +-/* keys to highlight the desired material in DF's material menu
2. Click to the LEFT of the FIRST letter of the highlighted material
3. Click to the RIGHT of the LAST letter of the highlighted material

Quickfort uses onscreen prompts and sound notifications to take you through
these steps.

The process lets Quickfort take a screen-clipping of the region between your
mouse-clicks. This clipping of the highlighted material's row is then used by
Quickfort as a "fingerprint" of your chosen material.

When QF encounters another cell with the same `:label` later, it will search
through the materials list, automatically moving the highlight and checking if
the "fingerprint" is found onscreen. When the correct material is again
highlighted, QF will use the material and continue.

__Important notes about memorization__

In memorization steps 2 and 3, you should normally click just OUTSIDE of the
highlighted material's name (to the left or right). This ensures that a
fingerprint taken of material "marble" is distinguishable from a fingerprint
for "marble bars"; if we had just clicked on the "m" and "e" in "marble", the
fingerprint for "marble" would also match "marble bars" since "marble" is
contained within "marble bars". By clicking OUTSIDE the letters, we include
the empty space before/after "marble" and thus will not confuse it with
"marble bars".

On step 3, note that for very long material names like
"petrified wood blocks", you should click to the LEFT of the Dist column
in the material menu instead (on the last letter of the material name before
the Dist column).

If QF mis-selects a material you memorized, try to click nearer the top and
bottom edges of your highlighted material during memorization. This will make
the fingerprint larger and thus less liable to later mis-identification.


Minecart tracks
---------------

Quickfort supports the designation of minecart tracks, stops, and rollers
through the normal mechanisms, e.g. a #build blueprint with `CS` in a cell
will designate a track stop.

For track segments (`CT...`), you must select from DF's menu to choose the
desired track segment, then send `{Enter}` to select it. For example, to
designate a "Track (E)" segment, which is the third item in the track
segments menu, you would use:

    CT{+ 2}{Enter}

To simplify such designations, a series of aliases have been created for
the various track-related designations. You can use these instead of the
aforementioned approach.

The aliases are:

    -- Track segments --
    trackN
    trackS
    trackE
    trackW
    trackNS
    trackNE
    trackNW
    trackSE
    trackSW
    trackEW
    trackNSE
    trackNSW
    trackNEW
    trackSEW
    trackNSEW

    -- Track/ramp segments --
    trackrampN
    trackrampS
    trackrampE
    trackrampW
    trackrampNS
    trackrampNE
    trackrampNW
    trackrampSE
    trackrampSW
    trackrampEW
    trackrampNSE
    trackrampNSW
    trackrampNEW
    trackrampSEW
    trackrampNSEW

    -- Horizontal and vertical roller segments --
    rollerH
    rollerV

    -- Track stops that dump to N/S/E/W --
    trackstopN
    trackstopS
    trackstopE
    trackstopW

For example, to create an E-W track with stops at each end
that dump to their outside directions, you could use the
following blueprint:

    #build Example track
    trackstopW trackEW trackEW trackEW trackstopE

See `Blueprints/Tests/minetracks.csv` for a larger example.


Command prompt
--------------

Quickfort's command prompt can be accessed with Alt+T. Here you can enter
commands as 'cells' to be played back. These can also be transformed with
Alt+R if desired; see the [Transformations section](#transformations).

Commands must be prefixed with the desired build phase, so that QF knows
how to handle your commands properly:

    // Dig a row of 4 cells
    Alt+T -> dig d,d,d,d

    // Build a big bridge
    Alt+T -> build ga(10x10)

    // Aliases
    Alt+T -> query booze

    // Build phase may be abbreviated
    Alt+T -> q booze

Here we dig out a tiny room, give it a bed and a door, place a food stockpile
in it, turn it into a bedroom, and set the stockpile to accept only booze:

    Alt+T ->   dig d,d,d,d
    Alt+T -> build b,`,`,d
    Alt+T -> place `,f,f,`
    Alt+T -> query r+,booze,`,`

Multirow 'blueprints' can also be entered at the command prompt by separating
lines with # like so:

    Alt+T -> dig d,d#d,d

    #dig Above command produces this result
    d d #
    d d #
    # # #

    Alt+T -> dig d,d#d,d##

    #dig Above command produces this result
    d d #
    d d #
    ` ` #
    # # #

Note in the second example how the command ends with ##. This is because the #
is treated as the end-of-row marker. If you want to add a final blank row to a
multirow command, therefore, you need to end with two #'s: one to end the
preceding line and another to end the last line.


Transformations
---------------

Quickfort supports repeating and transforming your blueprints in various ways.

Use the Alt+R hotkey to open the transformation prompt and see a simple syntax
primer. Enter ? to receive additional help.


Transformations: Simple repetition
----------------------------------

A blueprint can be repeated in any direction: north, south, east, west, up-z,
and down-z.

It can be repeated any number of times and repetitions can be
performed in 1, 2 or 3 dimensions.

The syntax is `#D ...` where # is the number of times to repeat and D is
the first letter of the direction you want to repeat in.

    Alt+R -> 3n
    Repeats the blueprint three times to the north

    Alt+R -> 4e 2s
    Repeats the blueprint 4x east and 2x south (8 repetitions total)

    Alt+R -> 2e 2s 2d
    Repeats the blueprint in a 2x2x2 cube pattern (multi-z-level)


Transformations: Simple transformation
--------------------------------------

A blueprint can be transformed in the following ways:

    Alt+R -> rotcw
    Rotates the blueprint 90 degrees clockwise.

    Alt+R -> rotccw
    Rotates the blueprint 90 degrees counterclockwise.

    Alt+R -> fliph
    Flips the blueprint horizontally (left edge becomes right edge).

    Alt+R -> flipv
    Flips the blueprint vertically (top edge becomes bottom edge).

    Alt+R -> flipv fliph
    Mirror the blueprint around both x and y axes.


Advanced transformations
------------------------

Repetition and transformation commands can be combined for some interesting
effects. To get the effect you want, however, you need to understand how
Quickfort 2.0's transformation engine works.

QF keeps track of two *transformation buckets* during transformation. We will
call these buckets the **Memory bucket**, or bucket A, and the
**Working bucket**, or bucket B.

Let's follow an example and observe how the buckets change as we execute the
following transformation sequence:

    #dig The blueprint we'll be transforming
    d d d #
    d ` ` #
    ` ` ` #
    # # # #

    Alt+R -> rotcw 3e flipv 2s rotccw

At the start of a transformation sequence, QF sets both buckets A and B to the
original, untransformed blueprint.

    Starting contents of transformation buckets (before any transformation):

        d d d    d d d
        d . .    d . .
        . . .    . . .
        --A--    --B--

QF then executes each command in the transformation sequence in order.

*Transformation commands* like `rotcw` affect *only* the Working bucket B. The
contents of B will be replaced with the transformed version of B.

    After rotcw transformation (only modifies B):

        d d d    . d d
        d . .    . . d
        . . .    . . d
        --A--    --B--

*Repetition commands* like `3e`, on the other hand, utilize both buckets A and
B. More specifically, A and B are *repeated in series* in the direction you
indicate. The result of that repetition then replaces the contents of both A and
B. If you specify `3e`, for example, you are actually getting the content of the
buckets in series as the result: ABA.

    After 3e repetition (ABA):

        d d d . d d d d d    d d d . d d d d d
        d . . . . d d . .    d . . . . d d . .
        . . . . . d . . .    . . . . . d . . .
        --------A--------    --------B--------

Once all transformations in the sequence have been performed, the contents of
*Working bucket B* are returned as the result, to be designated by Quickfort.

We have `flipv 2s rotccw` remaining to execute from our original transformation
sequence `rotcw 3e flipv 2s rotccw`. Let's execute the remaining steps and
see the result:

    After flipv transformation (only modifies B):

        d d d . d d d d d    . . . . . d . . .
        d . . . . d d . .    d . . . . d d . .
        . . . . . d . . .    d d d . d d d d d
        --------A--------    --------B--------

    After 2s (AB):

        d d d . d d d d d    d d d . d d d d d
        d . . . . d d . .    d . . . . d d . .
        . . . . . d . . .    . . . . . d . . .
        . . . . . d . . .    . . . . . d . . .
        d . . . . d d . .    d . . . . d d . .
        d d d . d d d d d    d d d . d d d d d
        --------A--------    --------B--------

    After rotccw (only modifies B):

        d d d . d d d d d    d . . . . d
        d . . . . d d . .    d . . . . d
        . . . . . d . . .    d d . . d d
        . . . . . d . . .    d d d d d d
        d . . . . d d . .    d . . . . d
        d d d . d d d d d    . . . . . .
        --------A--------    d . . . . d
                             d . . . . d
                             d d . . d d
                             -----B-----

    Returning B as finished result:

        d . . . . d
        d . . . . d
        d d . . d d
        d d d d d d
        d . . . . d
        . . . . . .
        d . . . . d
        d . . . . d
        d d . . d d
        -----------

Making sense yet? To get a better handle on how this all works, the best approach
is probably to just start experimenting with the Alt+R command. Also see
[transformation debugging](#advanced-transformations-debugging).

While it may seem unintuitive at first, this approach for transformation was
intentionally chosen for Quickfort 2.0. It is meant to retain the simple
QF1.x-style `2e 2s` repeat functionality, while also allowing the mixing of
QF1.x repetition commands with QF2.x transformation commands and allowing for
[interesting tesselations](#advanced-transformations-the-whirlpool-pattern).

_Author's note:_ I would be glad to hear of any suggestions for an alternative
approach/syntax here.


Advanced transformations: alignment
-----------------------------------

Consider the state our transformation buckets were in just before returning the
result in the preceding example:

    d d d . d d d d d    d . . . . d
    d . . . . d d . .    d . . . . d
    . . . . . d . . .    d d . . d d
    . . . . . d . . .    d d d d d d
    d . . . . d d . .    d . . . . d
    d d d . d d d d d    . . . . . .
    --------A--------    d . . . . d
                         d . . . . d
                         d d . . d d
                         -----B-----


Suppose we add a 2e onto the end of that transformation sequence:

    Alt+R -> rotcw 3e flipv 2s rotccw 2e

What do we get?

    . . . . . . . . . d . . . . d
    . . . . . . . . . d . . . . d
    . . . . . . . . . d d . . d d
    d d d . d d d d d d d d d d d
    d . . . . d d . . d . . . . d
    . . . . . d . . . . . . . . .
    . . . . . d . . . d . . . . d
    d . . . . d d . . d . . . . d
    d d d . d d d d d d d . . d d
    -----------------------------

You can see what has happened. A and B have been combined to repeat 2e,
but since their width and height differ from one another, Quickfort by default
aligns the two blueprints along their common bottom edge.

The horizontal and vertical alignment employed during transformation can be
controlled using the halign= and valign= commands in your transformation
sequence. Their syntax is:

    halign=left|middle|right|l|m|r (default: right)
    valign=top|middle|bottom|t|m|b (default: bottom)

Compare these results:

    Alt+R -> rotcw 3e flipv 2s rotccw valign=top 2e

    d d d . d d d d d d . . . . d
    d . . . . d d . . d . . . . d
    . . . . . d . . . d d . . d d
    . . . . . d . . . d d d d d d
    d . . . . d d . . d . . . . d
    d d d . d d d d d . . . . . .
    . . . . . . . . . d . . . . d
    . . . . . . . . . d . . . . d
    . . . . . . . . . d d . . d d
    -----------------------------

    Alt+R -> rotcw 3e flipv 2s rotccw valign=middle 2e

    . . . . . . . . . d . . . . d
    d d d . d d d d d d . . . . d
    d . . . . d d . . d d . . d d
    . . . . . d . . . d d d d d d
    . . . . . d . . . d . . . . d
    d . . . . d d . . . . . . . .
    d d d . d d d d d d . . . . d
    . . . . . . . . . d . . . . d
    . . . . . . . . . d d . . d d
    -----------------------------

    Alt+R -> rotcw 3e flipv 2s rotccw valign=b 2e

    . . . . . . . . . d . . . . d
    . . . . . . . . . d . . . . d
    . . . . . . . . . d d . . d d
    d d d . d d d d d d d d d d d
    d . . . . d d . . d . . . . d
    . . . . . d . . . . . . . . .
    . . . . . d . . . d . . . . d
    d . . . . d d . . d . . . . d
    d d d . d d d d d d d . . d d
    -----------------------------

Note that `2e`/`2w` repetitions are only affected by `valign`, and `2s`/`2n`
repetitions are only affected by `halign`. This is because we are specifying
alignment *along the shared axis* between the repeated sections. Thus
`valign=top 2s` doesn't do anything more than just `2s`, because it's the shared
*horizontal* axis between the northern and southern copy that they are aligned
along.

If you expect to do a lot of combined rotation and repetition to make
interesting patterns and variety in your fortress, strongly consider using
perfectly square blueprints (width == height), which when repeated in a
direction will adjoin nicely with neighboring designated blueprints. You'll
worry much less about halign/valign issues within complex transform sequences.


Advanced transformations: the whirlpool pattern
-----------------------------------------------

The so-called whirlpool pattern is the 'holy grail' for many symmetrical/fractal
layouts. It can make for very attractive and effective fortress layouts. The
design rotates a blueprint clockwise around a central point resulting in *4-fold
rotational symmetry*. (I [looked it up](http://en.wikipedia.org/wiki/Rotational_symmetry#n-fold_rotational_symmetry "Rotational symmetry").)

This can be accomplished using QF transformation, but with a twist (no pun
intended).

    #dig
    d d d #
    d ` ` #
    ` ` i #
    # # # #

You might expect that you could do it this way:

    Alt+R -> rotcw 2e rotcw 2s

But because the second `rotcw` only applies to Working bucket B, we end up with
this:

    d d d . d d
    d . . . . d
    . . i i . d
    . . . . d d
    . . . . . d
    . . . i . d
    . . . i . .
    . . . . . d
    . . . d d d
    -----------

Not quite what we're looking for.

What we can do instead of the second `rotcw` is to *flip* bucket B both
horizontally and vertically. When we then repeat `2s`, we repeat A and B (the
symmetrical mirror image of A) below (south of) it.

    Alt+R -> rotcw 2e fliph flipv 2s

    d d d . d d    }
    d . . . . d    } rows from A: rotcw 2e
    . . i i . d    }
    d . i i . .   }
    d . . . . d   } rows from B: rotcw 2e fliph flipv
    d d . d d d   }
    -----------

Voila.

Formula for the whirlpool pattern:

    Alt+R -> rotcw 2e fliph flipv 2s

This effect can be trivially made larger. Try these and compare the results:

    Alt+R -> rotcw 2e fliph flipv 2s 2e 2s

    Alt+R -> 2e 2s rotcw 2e fliph flipv 2s

For extra credit: how would you reverse the whirlpool transform to proceed in a
counterclockwise fashion (starting with `rotccw`)?


Advanced transformations: multiple Z-levels
-------------------------------------------

Z-level repetitions are treated as a special case in Quickfort. When included in
the transformation sequence, they are always executed last. Thus the following
produce identical results:

    Alt+R -> rotcw 2e 2s 10d
    Alt+R -> 10d rotcw 2e 2s

Z-level repetitions may be used in conjunction with multi-z-level blueprints.
See `Blueprints/Examples/screw-pump-tower-*.csv` for an example.

Using multiple #d/#u transformations in a single sequence is not well supported.
Prefer combining them into one transformation, e.g. `6d` instead of `3d 2d`.


Advanced transformations: the ! command
---------------------------------------

Normally transformations only apply to Working bucket B, leaving Memory bucket
A untouched. Sometimes you may want to have what is in bucket B copied to
bucket A. The `!` command performs this operation.

Compare the output of the two transformation sequences below:

    #dig
    d d d #
    d ` ` #
    ` ` i #
    # # # #

    Alt+R -> rotcw 2e

    d d d . d d
    d . . . . d
    . . i i . d
    -----------

    Alt+R -> rotcw ! 2e

    . d d . d d
    . . d . . d
    i . d i . d
    ------------

In the second example, we copied B to A *after* rotating B, but *before*
repeating 2e. We're essentially using the `!` command to "pre-rotate" A
before we perform our repetition.

Generally speaking, the `!` command can be thought of as a transformation
sequence separator. `rotcw ! 2e` is the same as executing the sequence `rotcw`,
then executing a separate sequence `2e` on the `rotcw` transformation's result.

    Alt+R -> rotcw 2e: rotate B, then repeat AB twice east
    Alt+R -> rotcw ! 2e: rotate the blueprint, then repeat it twice east


Advanced transformations: Search and replace
--------------------------------------------

The substitution command can be used to change the contents of cells using
a regular-expression based search and replace.

The syntax is:

    s/pattern/replacement/

For example, to change all `Ts` (stonefall trap) cells on a blueprint into
`Tw` (weapon trap) cells:

    Alt+R -> s/Ts/Tw/

`pattern` is a regular expression pattern; for more information please see
<http://www.regular-expressions.info/>. Most of the time, just using a
simple substring pattern will do what you expect.

`replacement` is the value to replace `pattern` with, and can be any valid
string. Use \1, \2, ... for regex capture-group matching.

Quickfort additionally supports two more useful features: matching empty
cells (`s//replacement/`) and match negation (`s/~pattern/replacement/`).

    Alt+R -> s//d/
    Matches all empty cells in a blueprint and fills them with `d`

    Alt+R -> s/~d/i/
    Turns all cells which do NOT match `d` into `i`

    Alt+R -> s/~/d/
    Turns all NON-empty cells into `d`

By default, Quickfort matches anywhere within the contents of a cell. Thus
the following:

    Alt+R -> s/oo/ee/

will turn cells containing `booze` into `beeze`. To require the entire cell
to match, use regex's `^` (match at start) and `&` (match at end) codes:

    Alt+R -> s/^oo&/ee/
    Used on cell `booze`, has no effect - cell stays as `booze`;
    used on cell `oo`, cell becomes `ee`

Quickfort only updates Working bucket B with `s/foo/bar/` commands. This
allows for making alternating patterns if desired. If this is not what
you want, either put the `s/foo/bar` commands *after* other transformation
commands, or follow it with a `!` command.

A few more examples:

    Alt+R -> s/Cw/Cw:foo/
    Adds manual material label `:foo` to all `Cw` cells

    Alt+R -> s/(Cw|Cf)/\1:foo/
    Adds manual material label `:foo` to all `Cw` or `Cf` cells

    Alt+R -> s/Cf/Cf:foo/ ! s/Cf:foo/Cf:bar/ 4e fliph flipv 4s
    Repeat a flooring blueprint as a checkerboard, using alternating manual mats


Advanced transformations: Change build phase
--------------------------------------------

Particularly when using the `s/pattern/replacement/` substitution command, it
can be useful to change the build phase without editing the blueprint directly.
This can be accomplished using the `phase=...` command.

For these examples, assume we start with a #dig blueprint. Observe:

    Alt+R -> phase=build
    Simply changes the #dig blueprint into a #build blueprint.

    Alt+R -> phase=build s/d/Cf/
    Sets as #build print, then changes all `d` cells into `Cf` (floor tiles).

    Alt+R -> phase=b s//Cw/ s/~Cw//
    Sets as #build, turns empty cells into `Cw` walls, and clears all others.

All build phases and their first-letter abbreviations are accepted.


Advanced transformations: debugging
-----------------------------------

By running `qfconvert.exe` or `qfconvert.py` from the command line, you can see
the progression of a particular transformation sequence and the contents of
buckets A and B after each step:

    > qfconvert.exe blueprints/Tests/transform-test.xls --mode=key --transform="rotcw 2e fliph flipv 2s" --show-transforms

or using abbreviated syntax:

    > qfconvert.exe blueprints/Tests/transform-test.xls -mkey -t "rotcw 2e fliph flipv 2s" -X

The use of `--mode=key` is just to avoid being spammed with DF-macro output
(very verbose).


Stupid dwarf tricks
-------------------

Dig a 2x2 column of up/down stairs deep into the earth:

    Alt+T -> dig i(2x2)
    Alt+R -> 100d

Undesignate a large chunk of the map on multiple z-levels:

    Alt+T -> dig x(100x100)
    Alt+R -> 10d

Undesignate (undo) a #dig or #place blueprint:

    Alt+R -> s/~/x/

Undesignate (undo) a #build blueprint (make sure you are in DF 'q' mode first):

    Alt+R -> phase=q s/~/x/

Manually choose and use the same material for all walls in a #build blueprint:

    Alt+R -> s/Cw/Cw:foo/

Add 'Cf' flooring in #build mode on top of each 'd' cell of a #dig blueprint:

    Alt+R -> phase=build s/d/Cf/ s/~Cf//


Troubleshooting
---------------

* Always check QF's mousetip instructions before hitting Alt+D to begin a
  blueprint. Being in the wrong menu is a common cause of wacky behavior.

* During DF macro playback, don't move the mouse into or out of the DF window
  (including ONTO the QF mousetip). Doing so will cause DF to stop playing
  your macro. It is usually safe to move the mouse (not too quickly) around
  the DF window itself.

* If you use a non-English keyboard layout, QF2 may require some tweaking first.
  The simplest solution is to switch to an English keyboard layout while running
  QF2. The nicer solution is to edit QF2's config/keys.json file to change how
  your keys are mapped, and replace QF2's config/interface.txt with your
  customized interface.txt from DF's data/init folder. keys.json maps QF commands
  to interface.txt's `[SYM:...]` and `[KEY:...]` entries. If needed, new entries
  can be added to keys.json and will be substituted the same as any other
  keys.json mapping entry.

* QF2 has no way of detecting when you run out of building materials during build
  mode. To compensate, QF2 sends (Shift+Enter, Down) repeatedly, and more often
  for larger size designations, to try and ensure that if we run out of a particular
  kind of mat we try to select from the other available mats.

  Some micromanagement of stockpile location or temporarily forbidding unwanted
  materials can help here.

* If a #build blueprint goes off the rails due to e.g. lack of mats, you
  can use the secret Alt+X hotkey while in DF's q menu. This causes QF to send x 30
  times to DF - an easy way to remove a large region of buildings quickly.

* Objects such as screw pumps and towers take special consideration in QF-based
  construction. See the `Blueprints/Examples/screw-pump-tower-*.csv` examples.
  For placing large areas of flooring for towers, consider using instructions
  like `Cf(10x10)`. QF doesn't account for what needs to be built in what order.
  Setting up multiple phases as separate worksheets/blueprints may help.

* Avoid running QF too close to the edges of the map; the outermost tiles of the
  map are unbuildable and can seriously derail a QF designation.


Create an Excel macro to size all columns to a uniform narrow width
-------------------------------------------------------------------

This tip can help when working with a lot of files.

We'll create a new Ctrl+T hotkey in your local Excel installation:

1.  In Excel, go to Tools->Macro->Record New Macro
2.  For macro name, enter: NarrowColumns
3.  For shortcut key enter: Ctrl+T (or your preference)
4.  Make sure it is set to store macro in Personal Macro Workbook.
5.  Hit OK.
6.  Click the gray corner cell in the very top left of the spreadsheet, between
    the row headers and the column headers. This should highlight the whole
    spreadsheet.
7.  Right click on column header A and select Choose Column Width.
8.  Type 2 and hit Enter.
9.  Go to Tools->Macro->Stop Recording.
10. Exit and restart Excel (this allows you to save your new macro).

Now, hit Ctrl+T in Excel at any time to size all columns of the current sheet to
a 2 unit width.


Other Excel tips
----------------

* Save your work in XLS or XLSX file formats. Unlike CSV files, XLS/X files will
  preserve any formatting you've done to your blueprints (column widths, cell
  coloring, etc.) and also make it easy to keep multiple build phases of a given
  design in a single XLS/X file as separate worksheets. In Excel, Ctrl+PgUp and
  Ctrl+PgDown switch between the worksheets in the current XLS/X file. Worksheets
  can be manipulated using the worksheet tabs at the bottom of the spreadsheet.

* To repeat a block of cells either across or down, highlight the cells, then
  drag the small square handle on the lower right corner of your
  selection box. Do this across then down to repeat over a large area.
  This often works better than copy and paste.

* You can determine the size of a selected region in Excel by selecting the
  cells with the mouse or shift+arrow keys, then before releasing the mouse
  button or shift key, look at the top left area just above column A's header.
  Note that the way Excel reports the numbers are the OPPOSITE of how they
  are used in QF. For example, if Excel reports 9R x 4C, you would want to
  enter something like f(4x9) in your file.


Links
-----

### Quickfort official links ###

* [Quickfort homepage](http://joelpt.net/quickfort)
* [Quickfort forum thread](http://www.bay12forums.com/smf/index.php?topic=35931.0)
* [Quickfort 2 source repository](https://github.com/joelpt/quickfort/)
* [Quickfort 2 issue tracker](https://github.com/joelpt/quickfort/issues?direction=desc&page=1&sort=created&state=open)
* [Community blueprints repository](http://www.mediafire.com/?oujvalbb0sggp)

### Visual designers for Quickfort ###

The following tools allow you to lay out multiple phases of a blueprint
visually, and output Quickfort compatible blueprint files.

* [DF Designer](http://www.bay12games.com/forum/index.php?topic=45433.0)
* [DFDrawCSV](http://www.bay12forums.com/smf/index.php?topic=80666.0)
* [Quickfort Assist](http://www.bay12forums.com/smf/index.php?topic=66755.0)
* [Quickfort Mapping Tool](http://www.nickskvarla.com/dwarf/)
* [WebFort](http://www.bay12forums.com/smf/index.php?topic=70957.0)

### Image-to-blueprint converters ###

The following tools convert image files (e.g. BMP) into Quickfort CSV files.

* [ChromaFort](http://www.bay12forums.com/smf/index.php?topic=55025.0)
* [image2qf](http://www.bay12forums.com/smf/index.php?topic=86813.0)
* [DF Architect](http://www.bay12forums.com/smf/index.php?topic=64723.0)

### Similar utilities to Quickfort ###

The following tools work similarly to Quickfort, operating on CSV blueprint
files.

* [LinDesignator](http://www.bay12forums.com/smf/index.php?topic=36928.0)
* [designator.ahk](http://www.bay12games.com/forum/index.php?topic=1428.0)

If you look hard you can still find a few remnants of designator.ahk in the
latest Quickfort.ahk source file!


Todo/Future Ideas
-----------------

* [COMPLETE] Refactor codebase
* Support 'transform'/'tx' keyword in QF command line
* [COMPLETE] Support multiline entries in QF command line
* Test/support every placeable DF object/command
* Support top/repeatable middle/bottom multilevel blueprints
* [COMPLETE] Support manual and automatic build material selection
* [COMPLETE] Rowwise large construction analysis (d,d\nd,d\n -> d(2x2))
* Consider support for all build phases in one CSV (d;b;;r+)
* Consider CSV 'stacks' - meta-blueprints acting as indexes to other CSVs
* Consider GUI for blueprint creation (incorporation of all mode-layers in an
  Excel-like GUI)
* Undesignate feature that undesignates based on a specific blueprint


Changelog
---------

### 2.04 (2012 May 29) ###

* Added support and aliases for mine tracks; see related section in README
* Verified compatibility with DF 0.34.10
* Conversion process is now 10-20x faster (the 'thinking' phase)
* Eliminated issues with 'cent' character being used in QFAHK code (Robik)
* Support aliases with expansion syntax, e.g. `trackNS(2x10)`
* Assume #dig for blueprints with no #phase top line (VenomIreland)
* Numerous other bug fixes and cleanup

### 2.03 (2012 January 10) ###

* Fixed problem with #query blueprints not playing back correctly

### 2.02 (2011 December 12) ###

* (EXPERIMENTAL) Manual material selection added! Windows only. See user manual
  for details, or try Blueprints/Tests/manual-bullseye.csv in Quickfort
* New transformation command: phase=... (changes blueprint build phase)
* New transformation command: s/pat/repl/ (search-and-replace cells with regex)
* On Windows, Quickfort will now check that [MACRO_MS:0] is set in the running
  DF's data/init/init.txt and offer to change it for the user if not
* Fixed issue with multilevel #build blueprints not plotting right (GoingTharn)
* Fixed issue with bridges and roads being given the wrong number of materials
  (they use #Tiles / 4 + 1 mats rather than just #Tiles)
* Added `qfconvert.py --mode=csv` output mode, to transform CSV files into new CSV files
* Switched to Python 2.7 and cxfreeze
* Commented options/buildconfig.json and options/keys.json for those who wish
  to read or modify these files
* Allow Alt+T commands to start with a #, e.g. #dig d,d,d
* Added config/matselect-(1,2,3).wav used during manual mat selection; these
  can be changed or removed
* Dropped EnableSafetyAbort option/function; QF now just checks that the
  DF window is focused before sending keystrokes, or waits until it is
* Various smaller fixes and tweaks

### 2.01 (2011 July 4) ###

* Added Alt+N "save named macro" function to QF GUI (Root Infinity)
* Set keys used by QF GUI for DF macro playback via options.txt (kurzedmetal)
* Macros produced by Alt+D will now be added to the bottom of DF's Ctrl-L list
  instead of the top, and include helpful titles
* Single-line QF command support for qfconvert.py via --command="dig d,d#d,d"
* Found that DF 0.31.25 will stop playing back any macro if you move your
  mouse pointer off the DF window (including ONTO Quickfort's mouse-tip).
  Warnings added to troubleshooting section and the QF GUI on-playback mousetip.
* qfconvert.py/exe will now find its config/ files regardless of working dir
* 2d/2u style z-repetitions are now performed after plotting/routing rather than
  beforehand; greatly improves speed of e.g. Alt+T->x(100x100), Alt+R->100d
* DF cursor is no longer returned to the starting z-level after a multi-z-level
  blueprint playback; that behavior was unintuitive
* Macro playback started faster (removed delays between ^L {Up} {Enter} ^P)
* QF GUI mousetip positioning tweaked
* readme.txt improvements (Thundercraft)
* blueprints/Tests/*.csv cleanup (Thundercraft) and a couple new ones
* Removed unused KeyExitMenu option from config/options.txt; this can now
  be configured in config/keys.json

### 2.00 (2011 June 21) ###

* Updated documentation (readme.txt) covering all new 2.00 features.

### 2.00pre5 (2011 June 19) ###

* Optimized how Alt+D works: we now only call qfconvert the first time a
  conversion needs to be performed, and will remember/reuse that result for
  subsequent uses of Alt+D.
* Made Alt+T command line's temp file not affect the remembered last
  file/folder.
* Made keysending start faster by reducing a few Sleep durations.
* Improved in-QFAHK Alt+R help text.
* Changed >> TRANSFORM: in tooltip to ALT+R: (more consistent with ALT+T text in
  command line mode and is a helpful key hint)
* Changed default PlaybackMode for new users from key to macro.
* options.txt tidy-up.


### 2.00pre4 (2011 June 17) ###

* Added Alt+T command line support with new multiline ability: dig d,d#d,d  digs a 2x2 area
* Full support for QF1-style aliases.txt is back.
* The included aliases.txt has been updated to work correctly with DF 0.31.25
  and a few new aliases were added. Please review the new config/aliases.txt as
  the format has changed slightly and a few aliases have been renamed for
  consistency.
* Alt+R gained new syntax: halign and valign. This solves the problem with non-
  square blueprints failing to work with e.g. rotcw 2e 2s.
* Build configuration, keycode mappings, and other config files externalized to config/ folder.
* Proper quote handling in CSV files (thanks bakergo).
* Various bug fixes, performance improvements, and UI tweaks.


### 2.00pre3 (2010 July 31) ###

* __Major rewrite__: The code structure and flexibility has been massively improved
  (no more single monster AHK script).
* __Linux/Mac support__: the code is now split into an AHK portion (*Windows
  only* GUI, for now) and a Python portion (cross platform blueprint
  conversion tool). Linux/OSX users can run `qfconvert.py` to convert blueprints to DF
  macro files.
* __Smarter playback__: Quickfort now tries to be smarter about its building
  strategy to minimize keystrokes, utilizing some simple pathfinding logic
  coupled with a strategy of constructing the largest areas possible.
* __DF macro support__: QF2.0 can convert blueprints to DF macro format (DF 0.31+).
  Set `[MACRO__MS:0]` in your `data/init/init.txt` for best performance. At least for
  this release, Alt+K in the QF GUI will toggle between macro and keystroke
  playback modes.
* __Excel support__: QF can now read blueprints in Excel formats (.xls, .xlsx). The
  Windows QF GUI supports selection of specific worksheets within Excel files.
  `qfconvert.py` also takes a `--sheetid` argument for this purpose.
* __GUI, revisited__: The Windows QF GUI has been redesigned. One important
  difference is that the function of the Alt+D key has changed. Alt+F is now
  used only for opening (changing) blueprint files; Alt+D is now used only for
  playing the current blueprint. This lets Alt+D work a bit more like a "stamp"
  tool; you can use Alt+F once and then Alt+D repeatedly. This is likely to
  catch up QF 1.x users at least once ;) but I think you'll come to like it
  quickly.
* __Repeat with transform__: The blueprint repetition functionality has been
  improved. A few transformations are now supported -- `rotcw, rotccw, fliph,
  flipv`. Read the embedded help when pressing Alt+R in QF GUI, or just
  experiment.
* __The /Modular project__: I've created a new subfolder in blueprints titled
  Modular. The blueprints in this folder are built from a common template
  (__template.xls) and are designed to be easily connected to adjacent Modular
  blueprints in a fortress. The intent is to build up a library of blueprints of
  various types that conform to this template. To that end, [color=yellow]I am
  looking for contributions[/color] if anyone would like to help populate this
  folder for future QF releases. Check out blueprints/Modular for more details.
  *NOTE: /Modular was later shelved for Quickfort 2.0's release; it will be back.*
* __Safer material selection__: For multi-cell constructions like a 10x10 floor,
  QF2.0 uses a more reliable material selection mechanism which should reduce
  the frequency of "out of this material" playback failures. Essentially it now
  hits +{Enter}{Down} during material selection `sqrt(# tiles in area)`
  times. This should make out-of-mat fails very infrequent, though you can end
  up building stuff out of multiple mat types if you don't take care with
  stockpile/mat proximity.
* __Multi-cell auto expansion__: Workshops and trade depots can now be constructed
  by populating all the blueprint cells that the object should occupy in the
  blueprint.


### 1.11 (2010 April 15) ###

* Addition of a "materials list" after loading a blueprint
  which can be very useful for the build phase
* Cancelling during a build now just shows a brief notice in the mousetip
  instead of popping up an annoying messagebox
* The 'switch to DF window' mousetip on QF startup has been removed;
  QF just appears when DF is active now and thus QF can now be put
  in Windows startup if desired
* Addition of startup tray tip and option ShowStartupTrayTip (default 1)
* Minor fixes/refactoring
* Added Repetition, Command prompt, and Stupid dwarf tricks to the readme

### 1.10 (2010 April 5) ###

* DF 0.31.01 supported; {ExitMenu} key-command now available in aliases.txt
* NOTE: Starting with QF 1.10, users of DF 40d# MUST edit QF's options.txt!!
* Fixed placement of farm plots
* Cleanup of options.txt
* Cleaned up and renamed .\Blueprints folder (was .\Examples)
* Modified mouse-tip positioning to avoid overlapping the pointer vertically

### 1.09 (2010 March 13) ###

* Multidimensional repetition support, e.g. 2 north 2 south 2 down
* Some refactoring

### 1.08 (2009 July 30) ###

* Yet another fix for safe sending mode; now using Send to send these keys.
* Alt+T will no longer retain start() setting from a previous .csv file

### 1.07 (2009 July 21) ###

* "Safe" key-sending mode added in 1.06 now uses a slow version of SendPlay
  instead of SendInput; safe mode is also now used whenever a modifier key or
  capital letter needs to be sent (they don't work w/ ControlSend & SendEvent)
* Improvements to keeping DF window focused and accepting keystrokes
* With these changes Quickfort appears to be fully working on DF 40d-40d13
* Visualization (Alt+V) now returns cursor to where it was beforehand
* "Switch to the DF window" tip now only shown when DF isn't active at QF start


### 1.06 (2009 July 3) ###

* Fix KeyUpZ/KeyDownZ not working right when using ControlSend mode; QF will now
  simply switch to the DF window and send these keystrokes using SendInput as needed


### 1.05 (2009 July 1) ###

* Big improvements to playback performance and reliability! Please update your options.txt.
* ControlSend send mode now makes window switching during playback possible (Valdemar);
  note pressing Alt/Ctrl/Shift/Win keys can still mess up playback sometimes
* DisableSafetyAbort now set by default since window switching is possible
* "Switch to DF window" mousetip now only shows once per run of QF

### 1.04 (2009 June 9) ###

* Added diagonal cursor movement optimization
* Fixed start() data from one blueprint carrying over to a subsequent blueprint w/o start()


### 1.03 (2009 June 7) ###

* start() position can now be overriden with Alt+Q/W/A/S.
* New option ShowOutOfWindowTooltip


### 1.02 (2009 June 3) ###

* Start position can now be specified in CSV file. See readme.txt for further
  details. Examples/Buketgeshud updated. (Xinael)
* Quickfort's tooltip now stays up all the time, but you can optionally hide it
  when not in placement or playback modes with the Alt+H hotkey (Xinael)
* The 'macro completed' popup has been removed in favor of the permanent tooltip
* Leading or trailing spaces within cells should no longer cause problems (LegoLord)
* Possible fix for flickering tooltip problem (Xinael)
* Possible speed improvement for 40d11/Mayday users (Xinael, Jhoosier)
* Z-level up/down default keybindings changed to Shift+5/Ctrl+5 for better
  compatibility (Jhoosier)
* Quickfort now emits a sound on playback completion (mutable in options.txt)


### 1.01 (2009 May 30) ###

* New options in options.txt to improve compatibility with different DF versions
  and key bindings (Xinael, Jhoosier)
* Auto cancel QF run if user switches away from DF window (Snuffy)


### 1.0 ###

* Initial release


Credits and License
-------------------

Quickfort is written by joelpt <quickfort@joelpt.net>.

Thanks to the following individuals whose code contributions are present
in Quickfort:

    bakergo (proper CSV file parsing; many good suggestions)
    Valdemar (author of designator.ahk, which QF 1.00 was based on)

Thanks to the following individuals whose bug-hunting or feature-requesting
resulted in improvements to Quickfort:

    Snuffy
    Xinael
    Jhoosier
    LegoLord
    shadow_slicer
    starrrie
    Aklyon
    Root Infinity
    Thundercraft
    kurzedmetal
    Robik
    VenomIreland

Copyright 2012 Joel Thornton

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
