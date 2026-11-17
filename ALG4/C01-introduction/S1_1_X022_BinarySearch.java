/*
 * File:          S1_1_X022_BinarySearch.java
 * Author:        Miquéias Alves Medeiros <https://github.com/miqu3iasg>
 * Created:       2026-11-09
 * Modified:      2026-11-09
 * Source:        Algorithm, 4th
 * By:            Robert Sedgewick, Kevin Wayne
 * Location:      p. 58
 *
 * Compilation:   $ javac S1_1_X022_BinarySearch.java
 * Execution:     $ java S1_1_X022_BinarySearch tinyW.txt < tinyT.txt
 *
 * 1.1.22 Write a version of BinarySearch that uses the recursive rank() given on page
 * 25 and traces the method calls. Each time the recursive method is called, print the argu-
 * ment values lo and hi, indented by the depth of the recursion. Hint: Add an argument
 * to the recursive method that keeps track of the depth.
 *
 * SPDX-License-Identifier: AGPL-3.0-only
 * Copyright:     (c) 2026 Miquéias Alves Medeiros <https://github.com/miqu3iasg>.
 */

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.Scanner;

public class S1_1_X022_BinarySearch
{
    public static int rank(int key, int[] a)
    {
        return rank(key, a, 0, a.length - 1);
    }

    public static int rank(int key, int[] a, int lo, int hi)
    {
        /*
         * TODO: I need to figure out how many times the funcition calls itself in the wholw
         * process and then apply this to a certain level of identation.
         */
        System.out.println("lo= " + lo + ", hi= " + hi);
        if (lo > hi) return -1;

        int mid = lo + (hi - lo) / 2;

        if  (key < a[mid]) return rank(key, a, lo, mid - 1);
        else if (key > a[mid]) return rank(key, a, mid + 1, hi);
        else return mid;
    }

    public static void main(String[] args) throws IOException
    {
        Scanner scanner = new Scanner(System.in);
        int[] whitelist = Files.lines(Path.of(args[0]))
                               .flatMap(line -> Arrays.stream(line.trim().split("\\s+")))
                               .mapToInt(Integer::parseInt)
                               .toArray();

        Arrays.sort(whitelist);

        while(scanner.hasNextInt())
        {
            int key = scanner.nextInt();
            if (rank(key, whitelist) < 0) System.out.println(key);
        }
    }
}
