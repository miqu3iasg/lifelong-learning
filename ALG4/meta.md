# ALG4 — Algorithms

## Overview

**Author:** Robert Sedgewick; Kevin Wayne  
**Edition:** 4th  
**Type:** book
**Subject:** Algorithms and Data Structures

_Algorithms_ presents a systematic study of fundamental algorithms and data structures, emphasizing implementation, mathematical analysis, and empirical evaluation of performance. The book covers foundational programming techniques, abstract data types, algorithm analysis, sorting, searching, graph processing, and string processing, followed by selected advanced topics. Its implementations use Java and an approach based on modular design and data abstraction.

The book adopts a scientific approach to algorithm development: formulate a problem, develop an algorithm, implement it, analyze its performance, and validate its behavior experimentally. It provides both theoretical foundations and practical implementations, making it suitable for developing a deeper understanding of algorithms and their applications.

## Bibliographic Reference

SEDGEWICK, Robert; WAYNE, Kevin. _Algorithms_. 4. ed. Upper Saddle River, NJ: Addison-Wesley, 2011. 976 p. ISBN 978-0-321-57351-3.

## Learning Objectives

By completing this book, I should be able to:

- Analyze the time and space complexity of algorithms using mathematical models, asymptotic notation, and empirical experiments.
- Implement and evaluate fundamental data structures, including stacks, queues, linked lists, symbol tables, search trees, heaps, and hash tables.
- Understand, implement, and compare fundamental sorting and searching algorithms, explaining their correctness, performance, and trade-offs.
- Represent and process graphs using fundamental traversal algorithms, minimum spanning tree algorithms, and shortest-path algorithms.
- Implement string-processing algorithms, including radix sorting, tries, substring search, regular expressions, and data compression techniques.
- Apply algorithmic problem-solving techniques to practical computational problems and select appropriate algorithms and data structures based on their requirements.
- Understand selected advanced topics, including event-driven simulation, B-trees, suffix arrays, network flow, reductions, and computational intractability.

## Conventions

This book follows the repository's general naming convention, with the adaptations that Java requires.

Java requires the name of a public class to match the name of its file, and class names cannot contain dots or dashes. Java files therefore use underscores in the section part and write the description in camel case, which is also the class name:

```text
S<m>[_<n>[_<p>]]_X<TTT>_<CamelCaseDescription>.java
```

Examples:

```text
S1_1_X024_EuclidsAlgorithm.java
S1_3_X001_FixedCapacityStack.java
S1_4_P001_ThreeSum.java
```

Notes written in Markdown keep the general repository format (for example, `S1_1_N001_basic_programming_model.md`).

Compiled `.class` files are produced in place, next to their sources, and are never versioned:

```text
javac S1_1_X024_EuclidsAlgorithm.java
java S1_1_X024_EuclidsAlgorithm
```

Book data files (for example, `tinyT.txt`, `tinyW.txt`) sit flat in the chapter directory, next to the exercise that uses them.

## Notes

This book is intended for readers with basic programming skills and familiarity with fundamental programming constructs. Previous exposure to data structures is helpful but not strictly necessary, since the book develops many of the relevant concepts from first principles.

Java is the primary programming language used throughout the book. Implementations and exercises should be treated as opportunities to understand algorithmic behavior, data representation, and performance rather than merely as programming tasks.

The study should emphasize understanding the underlying ideas, implementing algorithms independently, reasoning about correctness, and comparing theoretical complexity with observed performance. Mathematical concepts should be studied alongside their algorithmic applications, particularly asymptotic analysis, recursion, elementary probability where relevant, and graph theory.

The book's official companion website provides Java implementations, exercises, test data, lecture slides, visualizations, and additional learning resources.

## Links

- Official companion website — https://algs4.cs.princeton.edu/home/
- Official book page and resources — https://sedgewick.io/books/algorithms/
- Publisher's book page — https://www.pearson.com/en-us/subject-catalog/p/algorithms/P200000000597/9780132762564
- Complete table of contents — https://www.oreilly.com/library/view/algorithms-4th-edition/9780132762564/toc.html
- Java implementations and reference code — https://github.com/kevin-wayne/algs4
