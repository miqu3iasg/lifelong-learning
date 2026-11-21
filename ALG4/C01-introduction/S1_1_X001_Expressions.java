/*
 * File:          S1_1_X001_Expressions.java
 * Author:        Miquéias Medeiros <https://github.com/miqu3iasg>
 * Created:       2026-11-21
 * Source:        Algorithm, 4th
 * By:            Robert Sedgewick, Kevin Wayne
 * Location:      p. 58
 *
 * Compilation:   $ javac S1_1_X001_Expressions.java
 * Execution:     $ java S1_1_X001_Expressions
 *
 * Problem Statement:
 *     Paste the exercise/assignment text here.
 *
 * References:
 *   - https://...
 *
 * SPDX-License-Identifier: AGPL-3.0-only
 *
 * Copyright:     Copyright (c) 2026 Miquéias Medeiros <https://github.com/miqu3iasg>.
 */

public class S1_1_X001_Expressions
{

    public static void main(String[] args)
    {
        float a = (0 + 15) / 2; // => 7.5

        /*
         * The result was 7.0 actually. Java determines the type of operation based on the type of operands.
         * In other words, since it envolves operations with integers, the result is also produced an integer.
         *
         * See: https://docs.oracle.com/javase/specs/jls/se7/html/jls-15.html
         */
        System.out.println("Expressoin a) = " + a);

        // TODO: keeping solving exercises at the page 58
        float b = 2.0e-6 * 100000000.1;
        System.out.println("Expressoin b) = " + b);
    }
}
