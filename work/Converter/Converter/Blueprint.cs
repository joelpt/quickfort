using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Collections;
using Sun2.Collections;
using Sun2.ExtensionMethods;

namespace Converter
{
    public class Area
    {
        public int X, Y, Width, Height;
        public int Id;
        public bool Designated;
        public string Command;

        public int Size
        {
            get
            {
                return (X + Width - 1) * (Y + Height - 1);
            }
        }
    }

    public class Blueprint
    {
        public List<List<Area>> Areas;
        public int Height, Width;
        public bool RepeatableOnZ;

        int lastAreaId;


        public Blueprint(List<List<string>> commands, bool repeatableOnZ)
        {
            this.RepeatableOnZ = repeatableOnZ;
            this.Height = commands.Count; // Total rows = height
            this.Width = commands.Max(row => row.Count); // Longest row = width

            this.Areas = new List<List<Area>>(this.Height);
            this.lastAreaId = -1;


            // Initialize our List<List<T>>'s .. there must be a better way
            List<Area> emptyAreaInfos = new List<Area>(this.Width);
            for (int i = 0; i < this.Width; i++)
            {
                List<Area> row = new List<Area>(this.Width);

                for (int j = 0; j < this.Height; j++)
                {
                    row.Add(new Area()
                    {
                        Command = commands[i][j],
                        Designated = false,
                        Id = commands[i][j].IndexOf('[') >= 0   // isolate d[NxN] format cells
                            ? this.lastAreaId++
                            : -1,
                        X = i,
                        Y = j,
                        Width = 1,
                        Height = 1
                    });
                }
                this.Areas.Add(row);
            }
        }

        /// <summary>
        /// Assigns unique Areas to command cells which use the d[6x6] format,
        /// since they may not be made part of another area
        /// </summary>
        /*
         * void markMulticellCommands()
        {
            this.Areas =
                (
                    from row in Commands.Select((value, index) => new { value, index })
                    select
                     (
                         from cell in row.value.Select((value, index) => new { value, index })
                         select new AreaInfo()
                         {
                             Area = new Area()
                             {
                                 size = 1,
                                 Height = 1,
                                 Width = 1,
                                 X = cell.index,
                                 Y = row.index
                             },
                             Designated = false,
                             Id = cell.value.IndexOf('[') >= 0
                                 ? this.lastGroupAssignment++
                                 : this.GroupIds[row.index][cell.index]
                         }
                     ).ToList()
                ).ToList();
        }
        */

        public delegate Pair<T, U> PairDelegate<T, U>(T a, T b);


        bool cellMatchesCommand(int x, int y, string matchCommand)
        {
            if (x < 0 || y < 0 || x >= this.Width || y >= this.Height)
                return false; // Out of bounds

            if (this.Areas[y][x].Id > -1)
                return false; // Found a different group, can't be part of matchCommand's group

            if (this.Areas[y][x].Command != matchCommand)
                return false;  // Ran into a different command, can't be part of matchCommand's group

            return true;
        }

        void identifyBestAreas()
        {
            List<Area> newAreas;
            do
            {
                newAreas = assignAreas();
            } while (newAreas.Count > 0);
        }

        List<Area> assignAreas()
        {
            List<Area> assignedAreas = new List<Area>();
            //List<Pair<int, int>>[] edges = new List<Pair<int, int>>[this.Height];
            Dictionary<int, List<int>> edges = new Dictionary<int, List<int>>();

            // Get the list of largest areas that can be formed from each cell
            List<Area> areas = findLargestAreas();

            // Sort the list by descending area size
            areas = areas.OrderByDescending(a => a.Size).ToList();

            // Add each area to a list of 'will use' areas, and
            // also populate a list of lists of edge-pairs
            foreach (Area area in areas)
            {
                // Is some part of this area already assigned?
                int overlap = -1;
                overlap =
                    edges.First(row =>
                        row.Key >= area.Y &&
                        row.Key <= area.Y + area.Height - 1 &&
                        row.Value.Exists(i =>
                            i >= area.X &&
                            i <= area.X + area.Width
                        )
                    ).Key;
                
                // If it's overlapping, skip to the next area
                if (overlap >= 0)
                    continue;

                // add area
                assignedAreas.Add(area);

                // mark all Areas cells with what we've assigned
                int newId = this.lastAreaId++;

                for (int i = area.Y; i < area.Y + area.Height; i++)
                {
                    for (int j = area.X; j < area.X + area.Width; j++)
                    {
                        var a = this.Areas[i][j];
                        a.X = area.X;
                        a.Y = area.Y;
                        a.Width = area.Width;
                        a.Height = area.Height;
                        a.Id = newId;
                    }
                }

                // mark the four corners as permissible starting designation locations for this area

                this.GroupAreas[area.Y][area.X] = area;
                this.GroupAreas[area.Y][area.X + area.Width - 1] = area;
                this.GroupAreas[area.Y + area.Height - 1][area.X] = area;
                this.GroupAreas[area.Y + area.Height - 1][area.X + area.Width - 1] = area;

                // add areas' edge x-coordinates to edges[y..y+height-1]
                Pair<int, int> edge = new Pair<int, int>(area.X, area.X + area.Width - 1);
                for (int i = area.Y; i < area.Y + area.Height; i++)
                {
                    List<Pair<int, int>> edgesRow = edges[i];
                    if (edgesRow == null)
                        edgesRow = new List<Pair<int, int>>();
                    edgesRow.Add(edge);
                }
            }
            return assignedAreas;
        }

        List<Area> findLargestAreas()
        {
            List<Area> areas = new List<Area>();
            for (int x = 0; x < this.Width; x++)
            {
                for (int y = 0; y < this.Height; y++)
                {
                    areas.Add(findLargestAreaFrom(x, y));
                }
            }
            return areas;
        }

        private Area findLargestAreaFrom(int x, int y)
        {
            Area toEast = findLargestAreaInDirection(x, y, 1, 0);
            Area toSouth = findLargestAreaInDirection(x, y, 0, 1);
            if (toEast.Size >= toSouth.Size)
                return toEast;
            else
                return toSouth;
        }

        /// <summary>
        /// Find the largest area that can be made from a given (x,y) and initial delta of movement for
        /// checking adjacent squares.
        /// </summary>
        /// <param name="x">Cell x coordinate to be used as the top left corner of area</param>
        /// <param name="y">Cell x coordinate to be used as the top left corner of area</param>
        /// <param name="deltaX">Amount to increment X by in first pass, and Y by in 2nd pass
        /// One of deltaX or deltaY is expected to be 0</param>
        /// <param name="deltaY">Amount to increment Y by in first pass, and X by in 2nd pass</param>
        Area findLargestAreaInDirection(int x, int y, int deltaX, int deltaY)
        {
            // The terms width and height here are used dynamically: when deltaY != 0 they actually
            // refer to the opposite dimension relative to this.Commands' structure

            // Start counting matching cells in a line until we hit a nonmatch
            // or one that's already tagged with a GroupId
            int maxWidth = 1;
            string command = this.Areas[y][x].Command;
            while (maxWidth < (deltaX != 0 ? this.Width : this.Height))
            {
                if (cellMatchesCommand(x + (maxWidth * deltaX), y + (maxWidth * deltaY), command))
                {
                    maxWidth++;
                }
                else
                {
                    break;
                }
            }

            // Only 1 wide? If we could do a 1xN|N>1 block we'll do that in the other
            // call to this function (when DeltaX and DeltaY are swapped), so we can just
            // return a 1x1 area here now. If not, both calls will return 1x1 areas, which
            // would be accurate.
            if (maxWidth == 1)
                return new Area() { Height = 1, Width = 1, X = x, Y = y };

            // For each cell which is in the range of [x..x+maxWidth-1] find the
            // largest number of cells we can go south from it
            int maxHeight = 1;
            List<int> heights = new List<int>(maxWidth);

            for (int i = x; i < x + maxWidth; i++)
            {
                for (int j = y + (deltaX != 0 ? deltaX : deltaY); j < (deltaX != 0 ? this.Height : this.Width); j++)
                {
                    if (cellMatchesCommand(i, j, command))
                    {
                        maxHeight++;
                    }
                    else
                    {
                        break;
                    }
                }
            }

            // Find the minimum of the max-heights, that is, the furthest south
            // we can go from our starting (x,y) and still make a contiguous rectangle
            int minHeight = heights.Min();

            // Make a list of the valid contiguous areas that can be formed starting from (x,y)
            var validAreas =
              from cell in heights.Select((h, index) => new { height = h, width = index + 1 })
              where cell.height >= minHeight
              select new Area
              {
                  X = x,
                  Y = y,
                  Height = cell.height,
                  Width = cell.width,
                  Command = command
              };

            // Find the first area having the maximum area size.
            int largestAreaSize = validAreas.Max(area => area.Height * area.Width);
            Area largestArea = validAreas.First((Area a) => a.size == largestAreaSize);

            return largestArea;
        }

        /// <summary>
        /// Turns "d" into "", and "x" into "d", from this.Commands.
        /// Used for testing whether a strategy of digging the entire area first,
        /// then using x command to undig portions of it (subtractive digging strategy)
        /// would be more efficient
        /// </summary>
        /// <returns></returns>
        List<List<string>> invertDig()
        {
            var s =
                from row in this.Areas
                select (
                    from cell in row
                    select cell.Command == "" ? "x" : cell.Command == "d" ? "" : cell.Command
                    ).ToList();
            return s.ToList();
        }
    }
}
