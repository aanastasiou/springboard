# Springboard (sb)

Springboard is a Brainfuck pre-processor that adds the ability to define and re-use symbols.


## Quickstart

1. Any Brainfuck series of symbols (`{+, -, >, <, [, ], ., ,}`) is valid Springboard code
   - For example, the following is valid Springboard code:
     ```
        [-]+>[-]+[-<+>]
     ```

2. Springboard programs can define and re-use "symbols".
   - For example:
     ```
         : 0 [-];
         : 1 0 +;
         : add [-<+>];

         1>1 add
     ```
     This will compile to the addition snippet given at point #1 

3. Symbols can be defined locally (within a given file) or **imported**.
   - For example:
     - File: `mysymbols.sb`
       ```
           : 0 [-];
           : 1 0 +;
           : add [-<+>];

           1>1 add
       ```
     - File: `mycode.sb`
       ```
           import "mysymbols.sb"

           1>1>1>1>1
       ```
       
4. Comments start with `#` and extend to the end of the line.
   - For example:
     ```
     : 0 [-];     # Ensures that the value of a cell is set to zero
     : 1 0 +;     # Re-uses the symbol 0 to define 1.
     : add [-<+>] # Defines addition

     1>1 add      # Symbols get resolved recursively to produce the final code.
     ```


## Program structure

A typical Springboard program is divided into three *sections*:

1. Imports (optional)
   - One import per line
   
2. Symbol definitions (optional)
   - A symbol definition starts with `:`, followed by the symbol and terminates with `;`. 

3. Code (Mandatory)
   - Springboard code appears here as Brainfuck symbols intermixed with any defined symbols.


## "Libraries"

Springboard comes with a set of "libraries", that is, sets of predefined symbols, to:

1. Define numeric symbols (0,1,2,...)
2. Write stack based Brainfuck code



## Why Springboard?

The first implementation of what later became Springboard was, unsurprisingly in Forth. Forth's 
ability to define a "vocabulary" of "words" that resolve to effects on the stack(s) results in 
very readable and clear code. Taken to the extreme, the actual Forth code itself, spells out the
solution to a given problem.

I was playing around with writing a stack based Brainfuck program. So, I launched `gforth` and started 
defining a vocabulary of words that resolved to Brainfuck strings. That is, one actually writes a Forth program
that literally spells out the equivalent Brainfuck program.  Here is that very first `gforth` program:

```
```

*This programs evaluates to 0*.

This worked, but:

1. It required a Forth interpreter, for that one ability to define and re-use symbols.
2. A given Forth interpreter has its own semantics and would require some effort to "lock down" 
   the remaining Forth around Springboard. For example:
   1. Notice what `repnumber` looks like. `repnumber` implements a substitution like `5: +++++`. 
   2. Similarly, `import` woulc become a separate function which, because of the way Forth works, would have to 
      expressed as ` ." somefile " import`.

This gave birth to `Springboard`. What you find at the bottom of a mechanical dish stack. 
