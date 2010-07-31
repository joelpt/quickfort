using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;
using Sun2.Functional;

namespace Converter
{
    class Program
    {
        static void Main(string[] args)
        {
            List<int[]> ints = new List<int[]>();
            ints.Add((new int[] { 1, 2, 3 }));
            ints.Add((new int[] { 4, 5, 6 }));

            var result =
                from row in ints
                select (
                    from i in row
                    select i + 1
                    );


            foreach (var row in result)
            {
                foreach (int i in row)
                    Console.Write(i + " ");
                Console.WriteLine();

            }

            int[] numbers = { 5, 4, 1, 3, 9, 8, 6, 7, 2, 0 };

            var numsInPlace = numbers.Select((num, index) => new { Num = num, InPlace = (num == index) });
            var nums2 = numbers.Select((x, index) => new { x, index });

            var xx =
                from nums1 in numbers.Select((n, index) => new { n, index })
                select numbers[nums1.index];



            Console.WriteLine("\nPress any key to exit..");
            Console.ReadKey(false);


        }
    }
}
