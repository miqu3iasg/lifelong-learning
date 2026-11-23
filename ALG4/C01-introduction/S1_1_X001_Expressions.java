/*
 * File:          S1_1_X001_Expressions.java
 * Author:        Miquéias Medeiros <https://github.com/miqu3iasg>
 * Created:       2026-11-21
 * Source:        Algorithm, 4th
 * By:            Robert Sedgewick, Kevin Wayne
 * Location:      p. 58
 *
 * Compilation:   $ javac -d out S1_1_X001_Expressions.java
 * Execution:     $ java -cp out S1_1_X001_Expressions
 *
 * Give the value of each of the following expressions.
 *
 * SPDX-License-Identifier: AGPL-3.0-only
 *
 * Copyright:     Copyright (c) 2026 Miquéias Medeiros <https://github.com/miqu3iasg>.
 */

/**
 * Demonstrates the evaluation of arithmetic and logical expressions in Java.
 *
 * <p>Evaluates a set of expressions involving integer division, floating-point
 * arithmetic, scientific notation, and logical operators, illustrating how
 * Java determines expression results according to its language rules.
 *
 * @author Miquéias Alves Medeiros
 */
public class S1_1_X001_Expressions
{
    /**
     * Evaluates and prints the results of the expressions defined in the exercise.
     *
     * <p>Each expression illustrates a different aspect of Java expression
     * evaluation, including integer division, floating-point calculations,
     * operator precedence, and logical operations.
     *
     * @param args command-line arguments (not used)
     */
    public static void main(String[] args)
    {
        // a)
        float a = (0 + 15) / 2; // I think the result will be 7.5
        /*
         * The result was 7 actually. Java determines the type of operation based on the type of operands.
         * In other words, since it involves operations with integers, the result is also produced as an integer, and the
         * decimal part is discarded.
         *
         * See: https://docs.oracle.com/javase/specs/jls/se7/html/jls-15.html
         */
        System.out.println("Expressoin a) = " + a); // => Expression a) = 7

        // b)
        /*
         * The notation `2.0e-6` is scientific notation in Java, and it represents the number 0.000002. Both literals
         * are double, due to the double result. The mathematical result is 200.0000002.
         *
         * See: https://stackoverflow.com/questions/19984040/how-to-express-numbers-in-scientific-notation-in-java
         * See: https://docs.oracle.com/javase/8/docs/api/java/text/DecimalFormat.html
         */
        double b = 2.0e-6 * 100000000.1; // I can't calculate this by hand at all...
        System.out.println("Expressoin b) = " + b); // => Expressoin b) = 200.0000002

        // c)
        /*
         * In Java, `&&` has precedence over `||`. So, at first `true && false` results in `false`, and `true && true`
         * results in `true`.
         *
         * See: https://introcs.cs.princeton.edu/java/11precedence/
         */
        boolean c = true && false || true && true;
        System.out.println("Expression c) = " + c); // Expression c) = true
    }
}

