/*
 * File:          S1_1_X022_BinarySearch.java
 * Author:        Miquéias Alves Medeiros <https://github.com/miqu3iasg>
 * Created:       2026-11-09
 * Modified:      2026-11-21
 * Source:        Algorithm, 4th
 * By:            Robert Sedgewick, Kevin Wayne
 * Location:      p. 58
 *
 * Compilation:   $ javac -d out S1_1_X022_BinarySearch.java
 * Execution:     $ java -cp out S1_1_X022_BinarySearch tinyW.txt < tinyT.txt
 *
 * 1.1.22 Write a version of BinarySearch that uses the recursive rank() given on page
 * 25 and traces the method calls. Each time the recursive method is called, print the
 * argument values lo and hi, indented by the depth of the recursion. Hint: Add an argument
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

/**
 * Performs recursive binary search on a sorted array of integers.
 *
 * <p>Each recursive call is traced to standard output, displaying the current
 * search interval and its recursion depth. This implementation follows the
 * recursive binary search algorithm presented in Algorithms, 4th Edition.
 *
 * <p>The input is read from a whitelist file and standard input. The whitelist
 * is sorted before searching, ensuring the precondition required by binary search.
 *
 * @author Miquéias Alves Medeiros
 * @version 1.0
 * @since 1.0
 */
public class S1_1_X022_BinarySearch
{
    /**
     * Searches for a key in the entire array using recursive binary search.
     *
     * <p>This method initializes the search interval to cover the entire array
     * and delegates the search to the overloaded {@code rank()} method.
     *
     * @param key the integer value to search for
     * @param a the sorted array to search
     * @param depth the initial recursion depth
     * @return the index of the key if found; {@code -1} otherwise
     */
    public static int rank(int key, int[] a, int depth)
    {
        return rank(key, a, 0, a.length - 1, depth);
    }

    /**
     * Searches for a key within a specified interval using recursive binary search.
     *
     * <p>At each invocation, the method prints the current search interval
     * ({@code lo}, {@code hi}), indented according to the recursion depth.
     * It then compares the key with the middle element and recursively searches
     * the appropriate half of the interval.
     *
     * <p>The search terminates when the key is found or when the interval becomes
     * empty ({@code lo > hi}).
     *
     * @param key the integer value to search for
     * @param a the sorted array being searched
     * @param lo the lower bound of the current search interval, inclusive
     * @param hi the upper bound of the current search interval, inclusive
     * @param depth the current recursion depth, used to indent the trace output
     * @return the index of the key if found; {@code -1} if the key is absent
     *
     * @see <a href="https://algs4.cs.princeton.edu/14analysis/">Algorithms, 4th Edition, p. 25</a>
     */
    public static int rank(int key, int[] a, int lo, int hi, int depth)
    {
        /* See: https://stackoverflow.com/questions/28507978/recursion-depth-tabs-dents-in-java */
        String indent = "";

        for (int i = 0; i < depth; i++)
        {
            indent += "\t";
        }

        System.out.println(
            indent + "[" + depth + "] rank(lo=" + lo + ", hi=" + hi + ")"
        );

        if (lo > hi)
        {
            System.out.println(indent + "         -> Not found.");
            return -1;
        }

        int mid = lo + (hi - lo) / 2;

        if  (key < a[mid]) return rank(key, a, lo, mid - 1, depth + 1);
        else if (key > a[mid]) return rank(key, a, mid + 1, hi, depth + 1);

        else
        {
            System.out.println(indent + "         -> Found at index " + mid);
            return mid;
        }
    }

    /**
     * Reads the whitelist and search keys, then performs recursive binary searches.
     *
     * <p>The whitelist is loaded from the file specified by the first command-line
     * argument and sorted before any searches are performed. Search keys are read
     * from standard input until no more integers are available.
     *
     * <p>For each key, the method prints the search trace and the resulting index.
     *
     * @param args command-line arguments; {@code args[0]} must contain the
     *             path to the whitelist file
     * @throws IOException if an I/O error occurs while reading the whitelist
     * @throws ArrayIndexOutOfBoundsException if no whitelist path is provided
     */
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
            System.out.println("\nSearching for: " + key);
            int result = rank(key, whitelist, 0);
            System.out.println("\nResult=" + result);
        }
    }
}

