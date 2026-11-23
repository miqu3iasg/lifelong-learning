/*
 * File:          S1_1_X003_AreNumbersSame.java
 * Author:        Miquéias Medeiros <https://github.com/miqu3iasg>
 * Created:       2026-11-23
 * Source:        Algorithm, 4th
 * By:            Robert Sedgewick, Kevin Wayne
 * Location:      p. 58
 *
 * Compilation:   $ javac -d out S1_1_X003_AreNumbersSame.java
 * Execution:     $ java -cp out S1_1_X003_AreNumbersSame <a> <b> <c>
 *
 * Write a program that takes three integer command-line arguments and prints
 * equal if all three are equal, and not equal otherwise.
 *
 * SPDX-License-Identifier: AGPL-3.0-only
 *
 * Copyright:     Copyright (c) 2026 Miquéias Medeiros <https://github.com/miqu3iasg>.
 */

/**
 * Determines whether three integer command-line arguments are equal.
 *
 * <p>Reads three integers from the command line, compares their values,
 * and prints {@code "equal"} if all three are identical or
 * {@code "not equal"} otherwise.
 *
 * @author Miquéias Alves Medeiros
 */
public class S1_1_X003_AreNumbersSame
{
    /**
     * Determine wheter all three integers have the same value.
     *
     * <p>Compares each pair of numbers to verify that all three are equal.
     * Returns {@code true} if all numbers are identical, or {@code false}
     * otherwise.
     *
     * @param a the first integer
     * @param b the second integer
     * @param c the third integer
     * @return {@code true} if all three numbers are equal; {@code false} otherwise
     */
    public static boolean areTheNumbersTheSame(int a, int b, int c)
    {
        return a == b && b == c;
    }

    /**
     * Executes the program using three integer command-line arguments.
     *
     * <p>Validates the number of arguments, parses them as integers,
     * and prints whether all three values are equal.
     *
     * @param args command-line arguments containing three integers
     */
    public static void main(String[] args)
    {
        if (args.length != 3)
        {
            System.out.println("Usage: java S1_1_X003_AreNumbersSame <a> <b> <c>");
            return;
        }

        int a = Integer.parseInt(args[0]);
        int b = Integer.parseInt(args[1]);
        int c = Integer.parseInt(args[2]);
        boolean result = areTheNumbersTheSame(a, b, c);
        System.out.println("Result: " + result);
    }
}
