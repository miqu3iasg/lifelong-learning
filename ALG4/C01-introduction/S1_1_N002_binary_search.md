---
title: S1_1_N002_binary_search
tags:
    - content
    - algorithms
    - programming
description: An explanation about Binary Search algorithm.
authors: Robert Sedgewick, Kevin Wayne
source: Algorithms, 4th
source:
location: ch. 1, sec. 1.1, pp. 46-50
aliases:
    - binary search
date: 2026-11-21T11:07:00
id: 887ac034-281e-48b9-8d3b-19389eabbf0f
---

# Binary Search

The binary search algorithm is widely used. It is implemented in a static method (in the context of the Java programming language) called `rank()`, which takes an integer called `key` (our target number) and a _sorted_ array of `int` values as arguments. It returns the index of the key if it is present in the array; otherwise, it returns `-1`.

To accomplish this, two variables called `lo` and `hi` are used. They store the indices of the first and last elements of the search range, respectively.

Since the array is sorted, we can search for the target key within the range `[lo..hi]`. We calculate `mid` to find the middle index of this range and compare the element at that position with our target key. If the key is smaller than the middle element, we can discard the right half of the search range. Otherwise, we discard the left half. This process repeats until the target key is found or the search range becomes empty.

![Binary search in an ordered array](/home/miqu3iasg/dev/repos/studies/attachments/2026-11-21-11-19-15.png)

## Implementation

This program takes the name of a whitelist file (a sequence of integers) as argument and filters any entry that is on the whitelist from standard input, leaving only integers that are not on the whitelist on standard output. It uses the binary search algorithm, implemented in the static method rank(), to accomplish the task efficiently.

```java
import java.util.Arrays;
public class BinarySearch
{
    public static int rank(int key, int[] a)
    {
        // Array must be sorted.
        int lo = 0;
        int hi = a.length - 1;
        while (lo <= hi)
        {
            // Key is in a[lo..hi] or not present.
            int mid = lo + (hi - lo) / 2;
            if
            (key < a[mid]) hi = mid - 1;
            else if (key > a[mid]) lo = mid + 1;
            else
                return mid;
        }
        return -1;
    }
    public static void main(String[] args)
    {
        int[] whitelist = In.readInts(args[0]);
        Arrays.sort(whitelist);
        while (!StdIn.isEmpty())
        {
            // Read key, print if not in whitelist.
            int key = StdIn.readInt();
            if (rank(key, whitelist) < 0)
                StdOut.println(key);
        }
    }
}
```

## See Also

- [[S1_1_X022_BinarySearch.java]], resolution of the exercise 1.1.22 from p. 58. It implements binary search algorithm using recursive function calls and trace each call displaying the `lo` and `hi` values with depth indentation for each call.

# References

SEDGEWICK, Robert; WAYNE, Kevin. _Algorithms_. 4. ed. Upper Saddle River, NJ: Addison-Wesley, 2011. 976 p. ISBN 978-0-321-57351-3.
