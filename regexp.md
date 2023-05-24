# Regular Expression Collection

A note containing some (common) regular expression. you can add any (interesting or useful) regular languages that you like here to make it look like a nice collection of (useful) regular expressions. You can add any note for a reguarl expression if it's hard to understand.


- All strings except $11$:  
Ans: $\epsilon + 1 + 0 + 00 + 01 + 10 + (0 + 1)^3(0+1)^*$

- All strings of alternating $0$s and $1$s
Ans: $(\epsilon + 1)(01)^*(\epsilon + 0)$

- All strings that do not contain $000$ as a subsequence
Ans1: $1^*(\epsilon + 0)1^*(\epsilon + 0)1^*$  
Note2: all strings having at most two $0$s
Ans2: $1^* + 1^*01^* + 1^*01^*01^*$

- All strings that do not contain $010$ as a subsequence
Note: $1$ can't be in middle of two $0$s
Ans: $1^*0^*1^*$

- All strings that do not contain $10$ as a substring
Note: 0 must appear before 1
Ans: $0^*1^*$

- All strings that contain $101$ or $010$ as a substring  
Ans: $(0 + 1)^*(101 + 010)(0 + 1)^* $

- All strings that do not contain $111$ as a substring  
Note: appearance of $111$ should be avoid
Ans: $((\epsilon + 1 + 11)0)^*(\epsilon + 1 + 11)0^*$

Regular languages are closed under union, concatenation, kleene star, intersection

Languages accepted by DFAs are closed under complement, intersection and union

Languages accepted by NFAs are closed under concatenation, union, kleene star.

CFLs are closed under union, concatenation and Kleene star but not under intersection
