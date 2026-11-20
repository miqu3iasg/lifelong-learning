;;; File:          S1_1_7_X006_alternative_compute_squere_roots.scm
;;; Author:        Miquéias Medeiros <https://github.com/miqu3iasg>
;;; Created:       2026-11-20
;;; Source:        Structure and Interpreation of Computer Programs (SICP)
;;; By:            Harold Abelson, Gerald Jay Sussman, Julie Sussman
;;; Location:      p. 32
;;;
;;; Usage:
;;;   Run:      $ mit-scheme --quiet --load S1_1_7_X006_alternative_compute_squere_roots.scm
;;;   To evaluate line by line, use ,ee and ,er in the REPL.
;;;
;;; The exercise is stated below.
;;;
;;; References:
;;;   - https://stackoverflow.com/questions/22578975/primitive-procedures-and-special-forms-in-scheme
;;;   - https://groups.csail.mit.edu/mac/ftpdir/scheme-7.4/doc-html/scheme_3.html
;;;
;;; SPDX-License-Identifier: AGPL-3.0-only
;;;
;;; Copyright: Copyright (c) 2026 Miquéias Medeiros <https://github.com/miqu3iasg>.

#|
Exercise 1.6: Alyssa P. Hacker doesn’t see why if needs to be provided as a
special form. “Why can’t I just deﬁne it as an ordinary procedure in terms of
cond?” she asks. Alyssa’s friend Eva Lu Ator claims this can indeed be done,
and she deﬁnes a new version of if:
|#

; She just created a new if statement, it uses the same logic
(define (new-if predicate then-clause else-clause)
  (cond (predicate then-clause)
        (else else-clause)))

;; Eva demonstrates the program for Alyssa:

;; That is, 2 = 3? Yes, then return 0. No, then return 5.
(new-if (= 2 3) 0 5) ; => 5
;; that is, 1 = 1? Yes, then return 0. No, then return 5.
(new-if (= 1 1) 0 5) ; => 0

;; Delighted, Alyssa uses new-if to rewrite the square-root program:
(define (sqrt-iter guess x)
  (new-if (good-enough? guess x)
          guess
          (sqrt-iter (improve guess x) x)))

;; What happens when Alyssa attempts to use this to compute square roots?
;; Explain.

#|
This is the original piece of code cited by the exercise statement:

(define (sqrt-iter guess x)
  (if (good-enough? guess x)
    guess
    (sqrt-iter (improve guess x) x)))

It's just the same code, but using `new-if` inseated of `if`.

See: S1_1_7_P007_square_root_procedure_example.scm

For this case, I assume the result will be same even using the procedure insted
of use the special form `if`, because it's just all numbers. But if we dig into
the scheme interpreter, maybe we can find some dinstinctions. The scheme
interpreter uses applicative-order-evaluation, this means that it first expand
all the arguments and then evaluate the procedure property said. So, if we use
it in some recursive or error procedure, this can be annoying. For example:

(new-if (= 2 3)
        0
        (/ 1 0))

even though the predicate is false, the interpreter will be evaluate all the
values, including the indeterminacy, before evaluating the `new-if` procedure
itself. Consequentely, you get an zero division error.

but if you use the special form `if`, this won't happen, because it evaluates
only the selected branch by the predicate.

(new-if (= 2 3)
        0
        (/ 1 0)) ; => 0

The summary is: the special form evaluates the predicate first, and the
procedure evalutes all the arguments first.
|#
