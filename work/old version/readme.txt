Using the designation macro:

1. Create a spreadsheet. In it, use a blank cell for an unmined space, or a cell with a letter in it corresponding to the designation action you want to do. 
(See spreadsheet-example.png) It should be bordered in # signs.
The letters are the same as in-game. D=mine, I=up/down stair, etc.

2. Save as a .csv file. If your program asks you for a CSV dialect to save in, leave it as default.

3. Name your file roomdef#.csv, where # is a number 1-9 that you will use to access it from the macro

4. Run the macro (double click on the .ahk or .exe) 

5. Press Alt-#, where # is the number in the file name

6. Open the game. Go into the designation menu and move the cursor to the top-left corner of where you want your area. Press Alt-B to build the pattern.


For construction mode:

Save as Croomdef#.csv. Note the extra 'C' at the front
Press Alt-C before you run with Alt-B to go to construction mode. Alt-D will return to designation mode.
Your spreadsheet should have the construction hotkeys in it. w=wall, f=floor etc. 

Direction selectors:

Alt-Q : Tells the macro you will be indicating the top-left corner of the area (default)
Alt-W : Tells the macro you will be indicating the top-right corner of the area
Alt-A : ... the bottom-left corner
Alt-S : ... the bottom-right corner

Predefined definitions:

See roomdef1-result.png and roomdef2-result.png for the results of the two predefined definitions.