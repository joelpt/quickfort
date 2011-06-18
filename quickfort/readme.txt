Quickfort 2.00pre4
==================

*******************************************************************************************
*** NOTICE: The documentation in this file has been only partly updated since Quickfort 1.11
*** and is out of date. It will be updated before 2.00 'release' version.
*** Quick use guide for Quickfort 2.x:
***
*** ALL USERS:     I highly recommend setting [MACRO_MS:0] in your data/init/init.txt
***                for best DF macro playback performance.
*** Windows users: Run Quickfort.exe for the GUI interface
***                Run qfconvert.exe for the command line conversion tool
*** Linux users:   Run the command line conversion tool via python:
***                > cd src/qfconvert
***                > python ./qfconvert.py
***                or chmod +x qfconvert.py and run it like a shell script.
*** Linux/command line example:
***   > python ./qfconvert.py myblueprint.xls <DF folder>/data/init/macros/myblueprint.mak
***   ... then play your macro in DF with Ctrl+L, <select macro>, Ctrl+P.
***
*******************************************************************************************

by joelpt <quickfort@joelpt.net>, original idea by Valdemar

<http://sun2design.com/quickfort>

Quickfort 2 is a utility for Dwarf Fortress that helps you build fortresses from "blueprint" .CSV,
.XLS, and .XLSX files. Many applications exist to edit these files, such as MS Excel and Google
Docs. Most building-oriented DF commands are supported through the use of multiple files/worksheets
to describe the different phases of DF construction (designation, building, stockpiles, and making
adjustments).

Original idea and initial codebase from Valdemar's designator.ahk script
<http://www.bay12games.com/forum/index.php?topic=1428.0>.

User contributed blueprints can be found at <http://drop.io/quickfort>.


Features
--------

* Design complete blueprints to handle 4 main phases of DF construction
* Single-blueprint .CSV and multi-blueprint .XLS/.XLSX files supported
* Multi-Z-level blueprints
* Blueprint transformation and repetition
* Aliases to automate frequent keystroke combos
* Minimalist GUI with built-in command line mode (Windows only)
* Cross-platform (command line converter only, requires Python)
* DF macro or keystroke output methods supported
* Assortment of sample blueprints included

What's new in Quickfort 2.0
---------------------------

* Conversion engine rewritten in cross-platform Python
* New solver plots blueprints much more efficiently; ~4x faster playback than QF 1.x
* Use of DF macros for playback to DF; faster and more reliable than QF 1.x
* XLS/XLSX (Excel) workbooks support makes it easy to bundle multi-phase blueprints
* Improved Windows GUI, including enhanced blueprint info/select GUI and shrinkable mousetip
* Alt-R repeat syntax expanded to support basic transformations, e.g. fliph flipv 2e
* Alt-T command line supports multi-row entry, e.g. dig d,d#d,d
* Multi-cell buildings can be plotted in multiple cells instead of using e.g. wr(3x3)
* Build and keystroke logic configurable through config files

For users of Quickfort 1.x
--------------------------

A few things have changed in Quickfort's basic operation in the move from 1.0 to 2.0:

* Alt+D no longer opens a blueprint file AND plays it. Instead, Alt+F is now used to open a file,
  and Alt+D is used to play the file. This enables Alt+D to work a bit like a "stamp" tool, but
  may be disconcerting to experienced QF1 users at first.

* QF2 now outputs DF macros by default. These are faster and more reliable than QF1's key-sending
  approach, though that approach is still supported; use Alt+K to toggle modes. 
  Be sure to set [MACRO_MS:0] in your DF's data/init/init.txt or macro playback will be slow.

Windows Quick Start
-------------------

Linux/OSX Quick Start
---------------------

You must have Python 2.6.4 installed.

*** Linux users:   Run the command line conversion tool via python:
***                > cd src/qfconvert
***                > python ./qfconvert.py
***                or chmod +x qfconvert.py and run it like a shell script.
*** Linux example:
***   > python ./qfconvert.py myblueprint.xls <DF folder>/data/init/macros/myblueprint.mak
***   ... then play your macro in DF with Ctrl+L, <select macro>, Ctrl+P.


Basic Usage
-----------

Please see the Troubleshooting section for solutions to common problems.

Quickfort's GUI consists of a mouse tooltip, hotkeys and a few popup windows.
Quickfort does not need AutoHotkey installed.

Start Dwarf Fortress (windowed mode recommended). Run Quickfort.exe.

Use Alt+D to select a CSV file to execute. There are some samples in the
Blueprints folder. Quickfort will give instructions in the mouse tooltip for
positioning the in-game cursor. Once positioned, use Alt+D again to begin.
Quickfort will send the keystrokes necessary to DF to dig, build, place, or
query according to the chosen blueprint. Resist the urge to touch the mouse or
keyboard at this time.

Alt+Q/W/A/S can be used to change the starting corner for the blueprint (that
is, which corner of the blueprint you'll put the starting cursor at). The
current starting corner setting will be shown in the QF tooltip. These hotkeys
have no effect if the blueprint specifies a starting cursor position; see
the "Specifying a starting position" section below for more details.

Alt+R can be used to repeat a blueprint any number of times to the north, south,
east, west, up, and down. This can be useful for digging multilevel
staircases/shafts, repeating room complexes, etc. You can even specify multiple
directions to build in.

Alt+T opens the Quickfort command line. Here you can enter a single-line
QF-style command. Commands entered this way can be repeated with Alt+R as well.

Hold down Alt+C to cancel Quickfort's build routine partway through.

After a build completes, Alt+E can be used to redo the same blueprint again, or
use Alt+D again to select a new blueprint. Alt+H can be used to hide QF's
mouse tooltip when not building; all hotkeys will continue to work.

Shift+Alt+Z suspends/resumes Quickfort, useful if you find it to interfere with
other windows. Shift+Alt+X exits Quickfort.


Editing CSV Files
-----------------

The format of Quickfort-compatible .CSV files is straightforward. The format has
changed slightly from Valdemar's designator.ahk format, but should only require
minor editing/search-and-replacing to work with Quickfort.

Use Excel or Google Docs to edit these files if at all possible (be sure to save
as CSV file). The first line of the file should look like this:

    #dig This is a comment.

The keyword "dig" tells Quickfort we are going to be using the Designations menu
in DF. The following keywords are understood:

  dig     Designations menu (d)
  build   Build menu (b)
  place   Place stockpiles menu (p)
  query   Set building tasks/prefs menu (q)

Optionally following this keyword and a space, you may enter a comment. This
comment will appear by default after loading the CSV file with Quickfort
(Alt+D). You can use this space for explanations, attribution, etc. Newlines may
be entered by using \n.

Below this line begin entering the keys you want sent in each cell (it's assumed
you are using a spreadsheet editor here). For example, we could dig out a 3x5
room with an up/down staircase in the corner like so (spaces are used as column
separators here):

    #dig
    i d d d #
    d d d d #
    d d d d #
    d d d d #
    d d d d #
    # # # # #

Note the # symbols at the right end of each row and below the last row. These
are OPTIONAL, but can be helpful. If you omit them QF *should* render your
blueprint properly. If you run into problems (e.g. Excel saving 'blank' cells
and rows unnecessarily), use # symbols as shown above to clearly delineate the
area. These tell QF where the edges of your blueprint are.

Once the dwarves have that dug out, let's build a walled in bedroom within our
dug-out area:

    #build
    Cw Cw Cw Cw #
    Cw b  h  Cw #
    Cw       Cw #
    Cw Cw d  Cw #
    #  #  #  #  #

Note my generosity - I've placed a bed, chest and door here as well. Note that
you must use the full series of keys needed to build something in each cell,
e.g. Cw for each wall segment.

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
blueprint layouts.

With f(2x1), we've asked QF to place a Food stockpile 2 units wide by 1 high
unit, or f(2x1). QF sends the necessary keys to resize the placement region.
This also works properly in all modes, including build mode (floors Cf(10x10),
bridges ga(4x4), etc. that are sized with UMKH keys).

Lastly, let's turn the bed into a bedroom, and set the food stockpile to hold
only booze.

    #query
    ` ` ` ` #
    ` r+` ` #
    ` booze #
    # # # # #

In column 2, row 3 we have r+. This sends r+ keys to DF when the cursor is over
the bed, causing us to 'make room' and increase its size slightly just in case.

In column 2, row 4 is just "booze". booze is an alias keyword defined in the
included aliases.txt file. This particular alias sets a food stockpile to carry
booze only, by sending the keystrokes needed to navigate DF's stockpile settings
menu.

The Blueprints/General/bedroom-*.csv files provide a good simple example of a
4-layer QF blueprint. Check out aliases.txt for some helpful starting aliases.
Blueprints/TheQuickFortress/ provides a good detailed set of examples covering
some more complex designs.


Specifying a starting position
------------------------------

You can optionally specify a cursor starting position for a particular
blueprint, simplifying the task of blueprint alignment. This can be helpful
for blueprints that are based on a central staircase, for example.

To specify a cursor starting position, use the following modified format
for the header line of your CSV file:

    #mode start(X;Y;STARTCOMMENT) comment

where X and Y specify the starting cursor position (1;1 is the top left cell)
and STARTCOMMENT (optional) is a description displayed to the QF user of
where to position their cursor. This description appears in the pre-playback
mouse tooltip.

A couple examples:

    #dig start(3; 3; Center tile of a 5-tile square) Regular blueprint comment
    #build start(10;15)

When a start() parameter is found in a CSV file, the normal Alt+Q/W/A/S
keys will override (ignore) said parameter. Alt+E will un-ignore the start()
paramter.

See Blueprints/Tests/starting-position.csv for a simple example.
The Blueprints/TheQuickFortress/*.csv examples all utilize start().


Multilevel blueprints
---------------------

Multilevel blueprints are accommodated by separating Z-levels of the blueprint
with #> or #< at the end of each floor:

    #dig Stairs leading down to a small room below
    j ` #
    ` ` #
    #># #
    u d #
    d d #
    # # #


Layering blueprints
-------------------

A complete QF specification for a floor of your fortress may contain 4 or more
separate CSV blueprints, one for each "phase" of construction (dig/designate,
build, place stockpiles, building adjustments). These phases suggest a
convenient naming scheme for blueprints, as seen in the Blueprints/General folder:

    bedroom-dig.csv
    bedroom-build.csv
    bedroom-stockpile.csv
    bedroom-adjust.csv

The naming scheme is up to you, of course. A similar approach is used in the
Blueprints/TheQuickFortress folder.

After digging out an area, it's often helpful to dump all leftover stone in the
area before beginning the build phase. You may also wish to smooth/engrave the
area before filling it in.


Repetition
----------

A blueprint can be repeated in 1, 2 or 3 dimensions using the Alt+R
"Repeat" command. Quickfort will designate the blueprint any number of times
in the directions you specify.

Press Alt+R for a simple syntax primer.


Command prompt
--------------

Quickfort's command prompt can be accessed with Alt+T. Here you can enter a single
line of a blueprint to be played back (including aliases). Additionally, you can use
Alt+R to repeat a command in multiple directions.


Stupid dwarf tricks
-------------------

* Dig a 2x2 column of up/down stairs deep into the earth:

    Alt+T -> dig i,i

    Alt+R -> 2 south 100 down

* Undesignate a large chunk of the map on multiple z-levels:

    Alt+T -> dig x(100x100)

    Alt+R -> 10 down


Troubleshooting
---------------

* Always check QF's mousetip instructions before hitting Alt+D to begin a
  blueprint. Being in the wrong menu is a common cause of wacky behavior.

* If you have trouble just getting one of the sample files to work, take a look
  at options.txt. Slowing down QF's key sending delay or other adjustments can
  help with problems (DelayMultiplier, KeyPressDuration).

* If you use a non-English keyboard layout, QF may not work properly for you.
  The simplest solution is to switch to an English keyboard layout while running
  QF. The nicer solution is to edit QF's options.txt file and modify the bindings
  for KeyLeft, KeyRight, et al. to match your keybindings. QF uses AutoHotKey's
  keybinding syntax; see <http://www.autohotkey.com/docs/commands/Send.htm>

* QF has no way of detecting when you run out of building materials during build
  mode; it just blithely assumes that the first material that appears in DF's
  materials list while building will be sufficient. For constructions that take
  many materials such as a big retracting bridge gs(10x10), if sending
  Shift+Enter does not provide all the materials required to build, the script
  will go off the rails. Some micromanagement of stockpile location or
  temporarily forbidding unwanted materials can help here. Also see the
  UseLongConstructions option in options.txt.

* If the script goes off the rails for some reason, use Alt+C to cancel it. If
  you've built a bunch of beds but ran out before the script finished, for
  example, you can use the Alt+X key while in DF's q menu. This causes QF to
  send x 30 times to DF - an easy way to remove a large region of buildings
  quickly.

* If you cancel playback, DF may become unresponsive to your input. Tapping
  the ALT key usually fixes this.

* Workshops, depots, stores, furnaces, and others place from their CENTER tile,
  rather than their top left tile as specified in the CSV. Make sure to account
  for these offsets in your blueprint. When in doubt, try positioning the cursor
  in game, then switch to the object you want to place and observe which of its
  tiles it anchors from.

* Objects such as screw pumps and towers take special consideration in QF-based
  construction. See the screw pump tower examples. For placing large areas of
  flooring for towers, consider using instructions like Cf(10x10). QF doesn't
  account for what needs to be built in what order, it just proceeds across then
  down (A Z pattern). Setting up multiple CSV layers to dig/build in phases may
  help.

* Avoid running QF near the edges of the map, or set
  DisableBacktrackingOptimization=1 in options.txt.


Create an Excel macro to size all columns to a uniform narrow width
-------------------------------------------------------------------

This tip can help when working with a lot of CSV files.

1.  In Excel, go to Tools->Macro->Record New Macro
2.  For macro name, enter NarrowColumns
3.  For shortcut key enter Ctrl+T (or your preference)
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

Other Excel tips:

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


Todo/Future Ideas
-----------------

* Refactor codebase
* Support 'repeat' keyword in QF command line
* Support multiline entries in QF command line
* Test/support every placeable DF object/command
* Support top/repeatable middle/bottom multilevel blueprints
* Support manual and automatic build material selection, similar to DFWall
* Rowwise large construction analysis (d,d\nd,d\n -> d(2x2))
* Consider support for all build phases in one CSV (d;b;;r+)
* Consider CSV 'stacks' - meta-blueprints acting as indexes to other CSVs
* Consider GUI for blueprint creation (incorporation of all mode-layers in an
  Excel-like GUI)


<a name="changelog"/>
---------
Changelog
---------

1.11 (2010 April 15)

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

1.10 (2010 April 5)

* DF 0.31.01 supported; {ExitMenu} key-command now available in aliases.txt
* NOTE: Starting with QF 1.10, users of DF 40d# MUST edit QF's options.txt!!
* Fixed placement of farm plots
* Cleanup of options.txt
* Cleaned up and renamed .\Blueprints folder (was .\Examples)
* Modified mouse-tip positioning to avoid overlapping the pointer vertically

1.09 (2010 March 13)

* Multidimensional repetition support, e.g. 2 north 2 south 2 down
* Some refactoring

1.08 (2009 July 30)

* Yet another fix for safe sending mode; now using Send to send these keys.
* Alt+T will no longer retain start() setting from a previous .csv file

1.07 (2009 July 21)

* "Safe" key-sending mode added in 1.06 now uses a slow version of SendPlay
  instead of SendInput; safe mode is also now used whenever a modifier key or
  capital letter needs to be sent (they don't work w/ ControlSend & SendEvent)
* Improvements to keeping DF window focused and accepting keystrokes
* With these changes Quickfort appears to be fully working on DF 40d-40d13
* Visualization (Alt+V) now returns cursor to where it was beforehand
* "Switch to the DF window" tip now only shown when DF isn't active at QF start


1.06 (2009 July 3)

* Fix KeyUpZ/KeyDownZ not working right when using ControlSend mode; QF will now
  simply switch to the DF window and send these keystrokes using SendInput as needed


1.05 (2009 July 1)

* Big improvements to playback performance and reliability! Please update your options.txt.
* ControlSend send mode now makes window switching during playback possible (Valdemar);
  note pressing Alt/Ctrl/Shift/Win keys can still mess up playback sometimes
* DisableSafetyAbort now set by default since window switching is possible
* "Switch to DF window" mousetip now only shows once per run of QF

1.04 (2009 June 9)

* Added diagonal cursor movement optimization
* Fixed start() data from one blueprint carrying over to a subsequent blueprint w/o start()


1.03 (2009 June 7)

* start() position can now be overriden with Alt+Q/W/A/S.
* New option ShowOutOfWindowTooltip


1.02 (2009 June 3)

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


1.01 (2009 May 30)

* New options in options.txt to improve compatibility with different DF versions
  and key bindings (Xinael, Jhoosier)
* Auto cancel QF run if user switches away from DF window (Snuffy)


1.0

* Initial release
