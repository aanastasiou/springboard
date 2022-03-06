# Springboard (sb)

Springboard is a Brainfuck variant with the ability to define and re-use symbols, inspired by Forth.

Here is a barebones example of what the language looks like:


```
: add [-<+>] ;

++ > +++ add ,
```

Springboard uses Forth's syntax to define "symbols" that are substituted by *Springboard code* at runtime.




A typical sb program is divided into three parts:

1. Imports
2. Symbol definitions
3. Code

Symbol definitions

The first implementation of what later became Springboard was in fact in Forth. I wanted to 
turn Brainfuck's random access "tape" to a stack and use familiar "symbols" to write code.  

as an experiment in defining a vocabulary
whose result would be 
