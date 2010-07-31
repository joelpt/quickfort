This is Buketgeshud, or translated from Dwarvish, The Quick Fortress.

It is a set of basic CSV blueprints for Quickfort, demonstrating its
use in assembling an entire basic (if incomplete) fort.

Buketgeshud is designed around a 30x20 blueprint with a common central
staircase/corridor layout. Blueprints can be repeated in any direction to
connect in a modular fashion with adjacent 30x20 areas. A fortresswide
example recirculating waterfall/plumbing system is included as an overlay
if you're feeling hardcore.

This is generally how you might assemble this fortress from embark:

* Embark!

* Clear a 30 wide x 20 high region of trees on the surface. This should be
  uninterrupted flat ground with soil (so that we can place farms below).
  Deconstruct your wagon. Consider building Blueprints/General/embarding-build.csv
  and -stockpiles.csv first (outside of your 30x20 footprint).

* Run surface-1-dig.csv. You'll want to put the cursor in the middle of the
  30x20 cleared area (14 right, 8 down from the top left corner). This digs out
  stairs on the surface, a farm/depot/workshop level below, as well as the
  beginnings of an entrance moat. The beginnings of a 3rd Z-level are also dug
  out; don't build anything here if you'd like to put waterfall plumbing in
  later.

* Let the dwarves complete the dig.

* Run surface-2-build-basics.csv (beginning from the same starting position as
  you used in step 4). This puts down a basic set of workshops commonly needed
  soon after embark, a couple farm plots and a depot.

* Run surface-3-stockpiles.csv to designate some area-appropriate stockpiles on
  the surface and below. Position the cursor for this
  and all future Buketgeshud blueprints on the top left stair tile of the
  central staircase.

* Run surface-3-stockpiles.csv to designate some area-appropriate stockpiles on
  the surface and below. Position the cursor for this and all other Buketgeshud
  blueprints on the top left stair tile of the central staircase.

* Run surface-4-adjust.csv to adjust the stockpiles' settings and designate your
  plots to grow plump helmets (most likely).

* Run surface-5-build-doors.csv and surface-5-build-walls.csv as desired. If
  buildings walls, make sure to remove the placeholder wall-construction on the
  surface beforehand.

* Now is probably a good time to dig out the central shaft and tunnels for
  several Z-levels below our surface/depot level. Run basic-dig.csv. Place the
  designate cursor THREE Z-levels below the surface, where no digging has
  occurred yet. Hit Alt+R and repeat 6 down.

* Other purpose-specific blueprints (e.g. bedrooms-*.csv) can now be placed on
  any desired Z-level along our central shaft; all these blueprints are based
  off the central shaft/tunnel layout used in basic-dig.csv. Consider dumping
  rock on newly dug levels before running -build.csv blueprints.

* Optionally use basic-stockpiles.csv and basic-adjust.csv to designate
  booze-only stockpiles around the central stairs on every Z-level of the
  fortress.

* If desired, add a fortresswide waterfall system, bathing your dwarves in tile
  after tile of lovely waterfall mist as they go about their day. Dig
  waterfall-1-dig.csv on the Z-level immediately below your farm/depot level
  (you left it empty, didn't you?) and repeat dig plumbing-1-dig.csv on Z-levels
  below that. Repeat for plumbing-2-build.csv and waterfall-2-build.csv in that
  order - see the blueprints' comments for complete details. You'll also need a
  reservoir at the bottom (not included).
