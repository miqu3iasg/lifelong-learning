# DSAX — Data Structures and Algorithms Exercises

<!-- Written once, when the source is created, and never updated again.
     Progress is derived from the structure: the highest exercise number
     with content is the progress. -->

## Overview

**Type:** problem set
**Author:** LeetCode
**Subject:** Data Structures and Algorithms

_Data Structures and Algorithms Exercises_ is a self-directed practice track
built on LeetCode's problem set. It covers the fundamental data structures — arrays,
strings, linked lists, stacks, queues, hash tables, trees, heaps, and graphs —
and the algorithmic techniques used to operate on them: searching, sorting,
two pointers, sliding windows, recursion, divide and conquer, backtracking,
greedy algorithms, dynamic programming, and graph traversal.

Each problem is solved independently in Java, with emphasis on correctness,
complexity analysis, and recognizing reusable patterns rather than memorizing
solutions.

## Bibliographic Reference

LEETCODE. Problemset. [S. l.]: LeetCode, [s. d.]. Disponível em:
https://leetcode.com/problemset/. Acesso em: 20 nov. 2026.

## Learning Objectives

By completing this source, I should be able to:

- Implement and use the fundamental data structures covered by the problem set.
- Analyze the time and space complexity of a solution and justify its trade-offs.
- Apply core algorithmic techniques, including two pointers, sliding windows,
  binary search, recursion, divide and conquer, backtracking, greedy algorithms,
  dynamic programming, breadth-first search, and depth-first search.
- Recognize which data structure or algorithmic pattern fits a problem and
  explain why.
- Write correct, readable, and efficient Java solutions, including edge-case
  handling and local tests.
- Communicate the reasoning behind a solution, not only the final code.

## Conventions

LeetCode is a problem platform, not a linear course, so this source has no unit
directories. Each problem is one Java file directly in the source root:

```text
S00_X<NNN>_<CamelCaseTitle>.java
```

- `S00` is used because problems are not tied to a section of the platform.
- `<NNN>` is sequential in the order problems are solved, not the LeetCode
  problem number. The original problem URL belongs in the file header's
  `Source` field.
- The slug is camel case and matches the public class name, as Java requires.
- The LeetCode `Solution` class stays package-private and is instantiated by the
  file's `main` method, which demonstrates the solution on an example.
- Compile and run each problem into its own output directory, because every
  problem defines a class named `Solution`:

```text
javac -d out/S00_X001_TwoSum S00_X001_TwoSum.java
java -cp out/S00_X001_TwoSum S00_X001_TwoSum
```

`out/` holds compilation byproducts and is never versioned. Java 21 is the
reference runtime.

Problem statements are not copied into the repository; the header links to the
original statement.

## Links

- LeetCode — https://leetcode.com/
- Problemset — https://leetcode.com/problemset/
- Study plans — https://leetcode.com/studyplan/
- Discussion forum — https://leetcode.com/discuss/
- Java 21 API — https://docs.oracle.com/en/java/javase/21/docs/api/
