/*
 * File:          S00_X001_TwoSum.java
 * Author:        Miquéias Medeiros <https://github.com/miqu3iasg>
 * Created:       2026-11-20
 * Source:        https://leetcode.com/problems/two-sum/description/
 *
 * Compilation:   $ javac -d out/S00_X001_TwoSum S00_X001_TwoSum.java
 * Execution:     $ java -cp out/S00_X001_TwoSum S00_X001_TwoSum
 *
 * References:
 *   - https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/HashMap.html
 *
 * SPDX-License-Identifier: AGPL-3.0-only
 *
 * Copyright:     Copyright (c) 2026 Miquéias Medeiros <https://github.com/miqu3iasg>.
 */

import java.util.Arrays;
import java.util.HashMap;

/**
 * Demonstrates a solution to the Two Sum problem.
 *
 * <p>Creates an input array, invokes the solution, and prints the resulting
 * indices to standard output.
 *
 * @author Miquéias Medeiros
 * @version 1.0
 * @since 1.0
 */
public class S00_X001_TwoSum
{
    public static void main(String[] args)
    {
        Solution sol = new Solution();
        int[] result = sol.solve(new int[] {2, 7, 11, 15}, 9);
        System.out.println(Arrays.toString(result));
    }
}

/**
 * Provides a solution to the Two Sum problem using a hash map.
 *
 * <p>Given an array of integers and a target value, finds the indices of
 * two distinct elements whose sum equals the target.
 *
 * <p>The algorithm traverses the array once, storing previously visited
 * numbers and their corresponding indices in a hash map. For each element,
 * it calculates the complement required to reach the target. If the
 * complement is already present in the map, the corresponding pair of
 * indices is returned.
 *
 * @author Miquéias Medeiros
 * @version 1.0
 * @since 1.0
 */
class Solution
{
    /**
     * Finds the indices of two numbers whose sum equals the target.
     *
     * <p>For each element, calculates its complement using
     * {@code target - nums[i]}. If the complement exists in the hash map,
     * returns its previously stored index together with the current index.
     * Otherwise, stores the current number and its index for subsequent
     * iterations.
     *
     * @param nums the input array of integers
     * @param target the target sum
     * @return an array containing the indices of the two elements whose
     *         sum equals the target
     * @throws IllegalArgumentException if no valid pair is found
     */
    public int[] solve(int[] nums, int target)
    {
        HashMap<Integer, Integer> seen = new HashMap<Integer, Integer>();
        for(int i = 0; i < nums.length; i++)
        {
            /*
             * The basic logic here is (considering the numbers 2, 7, 11, 15):
             *
             * First iteration:
             *
             * The current number is 2 at index 0.
             *
             * int complement = 9 - 2; // 7
             *
             * Does seen contain the number 7? No.
             * So, add the current number and its index to the HashMap:
             *
             * seen.put(2, 0);
             *
             * Second iteration:
             *
             * The current number is 7 at index 1.
             *
             * int complement = 9 - 7; // 2
             *
             * Does seen contain the number 2? Yes.
             * We previously stored it at index 0.
             *
             * Therefore, return the index of the previously stored number
             * and the index of the current number:
             *
             * return new int[] { 0, 1 };
             */
            int complement = target - nums[i];
            if (seen.containsKey(complement)) return new int[] { seen.get(complement), i };
            seen.put(nums[i], i);
        }
        throw new IllegalArgumentException("No solution found.");
    }
}

