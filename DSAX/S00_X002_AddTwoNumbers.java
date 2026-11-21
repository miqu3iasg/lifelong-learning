/*
 * File:          S00_X002_AddTwoNumbers.java
 * Author:        Miquéias Medeiros <https://github.com/miqu3iasg>
 * Created:       2026-11-20
 * Source:        https://leetcode.com/problems/add-two-numbers/description/
 *
 * Compilation:   $ javac -d out/S00_X002_AddTwoNumbers S00_X002_AddTwoNumbers.java
 * Execution:     $ java -cp out/S00_X002_AddTwoNumbers S00_X002_AddTwoNumbers
 *
 * SPDX-License-Identifier: AGPL-3.0-only
 *
 * Copyright:     Copyright (c) 2026 Miquéias Medeiros <https://github.com/miqu3iasg>.
 */

public class S00_X002_AddTwoNumbers
{

    public static void main(String[] args)
    {
        Solution sol = new Solution();
        System.out.println(sol.solve(/* args */));
    }
}

/* Definition for singly-linked list. */
class ListNode
{
    int val;
    ListNode next;

    ListNode() {}

    ListNode(int val)
    {
        this.val = val;
    }

    ListNode(int val, ListNode next)
    {
        this.val = val;
        this.next = next;
    }
}

class Solution
{
    public ListNode solve(ListNode l1, ListNode l2)
    {
        // TODO: implement
    }
}
