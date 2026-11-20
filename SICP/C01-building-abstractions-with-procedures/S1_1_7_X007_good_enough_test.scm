;;; File:          S1_1_7_X007_good_enough_test.scm
;;; Author:        Miquéias Medeiros <https://github.com/miqu3iasg>
;;; Created:       2026-11-20
;;; Source:        Structure and Interpreation of Computer Programs (SICP)
;;; By:            Harold Abelson, Gerald Jay Sussman, Julie Sussman
;;; Location:      p. 33
;;;
;;; Usage:
;;;   Run: $ mit-scheme --quiet --load S1_1_7_X007_good_enough_test.scm
;;;   To evaluate line by line, use ,ee and ,er in the REPL.
;;;
;;; Exercise 1.7: The good-enough? test used in computing square roots will not
;;; be very eﬀective for ﬁnding the square roots of very small numbers. Also,
;;; in real computers, arithmetic operations are almost always performed with
;;; limited precision. This makes our test inadequate for very large numbers.
;;; Explain these statements, with examples showing how the test fails for
;;; small and large numbers. An alternative strategy for implementing
;;; good-enough? is to watch how guess changes from one iteration to the next
;;; and to stop when the change is a very small fraction of the guess. Design a
;;; square-root procedure that uses this kind of end test. Does this work better
;;; for small and large numbers?
;;;
;;; References:
;;;   -
;;;
;;; SPDX-License-Identifier: AGPL-3.0-only
;;;
;;; Copyright: Copyright (c) 2026 Miquéias Medeiros <https://github.com/miqu3iasg>.


;;; This is the cited code (see S1_1_7_P007_square_root_procedure_example.scm):

;; In code, we can write this
(define (sqrt-iter guess x)
  (if (good-enough? guess x)
    guess
    (sqrt-iter (improve guess x) x)))

;; A guess is improved by averaging it with the quotient of the radicand
;; and the old guess
(define (improve guess x)
  (average guess (/ x guess)))

;; where average is
(define (average x y)
  (/ (+ x y) 2))

;; And we need also to define what is "good enough". The idea is improve the answer till
;; it is close enough so that its square diﬀers from the radicand by less than
;; a predetermined tolerance (here is 0.001)
(define (square x) (* x x ))

#|
A pseudo-code would be:

func is_good_enough(guess, x)
{
  return (guess**2 - x) > 0.001 # this make no fuking sense..
}
|#
(define (good-enough? guess x)
  ;; I don't have a clue about "abs" is
  (< (abs (- (square guess) x)) 0.001))

;; TODO: figure out how the test `good-enough` would be in a pseudo-code.

;; Finally, we need a way to get started. For instance, we can always guess
;; that the square root of any number is 1
(define (sqrt x)
  (sqrt-iter 1.0 x))
