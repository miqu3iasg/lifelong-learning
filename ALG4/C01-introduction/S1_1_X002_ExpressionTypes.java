/*
 * File:          S1_1_X002_ExpressionTypes.java
 * Author:        Miquéias Medeiros <https://github.com/miqu3iasg>
 * Created:       2026-11-23
 * Source:        Algorithm, 4th
 * By:            Robert Sedgewick, Kevin Wayne
 * Location:      p. 58
 *
 * Compilation:   $ javac -d out S1_1_X002_ExpressionTypes.java
 * Execution:     $ java -cp out S1_1_X002_ExpressionTypes
 *
 * Give the type and value of each of the following expressions.
 *
 * SPDX-License-Identifier: AGPL-3.0-only
 *
 * Copyright:     Copyright (c) 2026 Miquéias Medeiros <https://github.com/miqu3iasg>.
 */

/**
 * Demonstrates Java expression evaluation and type determination.
 *
 * <p>Evaluates a set of arithmetic, relational, and string concatenation
 * expressions, illustrating how Java determines expression types and
 * evaluates operations according to operator precedence and numeric
 * promotion rules.
 *
 * @author Miquéias Alves Medeiros
 */
public class S1_1_X002_ExpressionTypes
{
    /**
     * Evaluates and prints the results of the expressions defined in the exercise.
     *
     * <p>Each expression demonstrates a different aspect of Java's type
     * system, including numeric promotion, arithmetic evaluation,
     * relational operations, and string concatenation.
     *
     * @param args command-line arguments (not used)
     */
    public static void main(String[] args)
    {
        // a)
        /*
         * The result is a decimal number. Since the addition is within parentheses, that operation is performed first,
         * resulting in a proper decimal number. Then, the division is performed, and, mathematically, a division made
         * between a decimal number and an integer results in another decimal number. In Java, this is managed by
         * a mechanism called numeric promotion, which converts smaller, less precise numbers into larger or more precise
         * numbers.
         *
         * See: https://stackoverflow.com/questions/576302/what-is-numeric-promotion
         * See: https://docs.oracle.com/javase/specs/jls/se7/html/jls-5.html
         */
        double a = (1 + 2.236) / 2;
        System.out.println("Expression a) = " + a); // => Expression a) = 1.618

        // b)
        /* The same case as the previous one (see above). */
        double b = 1 + 2 + 3 + 4.0;
        System.out.println("Expression b) = " + b); // => Expression b) = 10.0

        // c)
        /* This is mathematically obvious. */
        boolean c = 4.1 >= 4;
        System.out.println("Expression c) = " + c); // => Expression c) = true

        // d)
        /*
         * This case is about string concatenation: at first, we have a simple addition, and then we get the result
         * of this addition and concatenate it with a string "3", resulting in the output "33", which is a String and not
         * a number, by the way. Since one of the operands is a string, Java performs a concatenation and not a sum. The
         * path is `1 + 2 + "3" => 3 + "3" (concatenation) => "33"`.
         */
        String d = 1 + 2 + "3";
        System.out.println("Expression d) = " + d); // => Expression d) = "33"
    }
}

