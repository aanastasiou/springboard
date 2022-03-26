# Springboard (sb)

Springboard is a Brainfuck pre-processor that adds the ability to define and re-use symbols.


## Quickstart

1. Plain Brainfuck code is valid Springboard code
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
     This will compile to the addition snippet given at point #1.
   - Notice here, "0" and "1" are NOT numbers.

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
         : 0 [-];      # Ensures that the value of a cell is set to zero
         : 1 0 +;      # Re-uses the symbol 0 to define 1.
         : add [-<+>]; # Defines addition

         1>1 add       # Symbols get resolved recursively to produce the final code.
     ```


## Program structure

A typical Springboard program is divided into three *optional sections*:

1. Imports
   - One import per line
   
2. Symbol definitions
   - A symbol definition starts with `:`, followed by the symbol, the Springboard code 
     it resolves to and terminates with `;`.
   - Symbol definitions in a given program can be imported to another program via the 
     use of `import`. 

3. Code
   - Springboard code appears here as Brainfuck code symbols intermixed with any defined symbols.

For more information, see [`examples/`](examples/)


## "Libraries"

Springboard comes with a set of predefined symbols ("libraries") that make writing stack based 
brainfuck much easier than writing plain brainfuck.

These help to define basic functions to:

- Define integers (`std/num_base_N.sb`, where `N` is `2,4,8,..256`, see for example [`std/num_base_256.sb`](std/num_base_256.sb))
- Define and manipulate strings ([`std/str.sb`](std/str.sb)) 
- Apply basic mathematical operations ([`std/math.sb`](std/math.sb)) 
- Apply basic stack operations ([`std/stack.sb`](std/stack.sb))
- Apply basic logic operations ([`std/logic.sb`](std/logic.sb))


## The Springboard compiler (`sbc.py`)

This repository includes the Springboard compiler, a Python program that reads `.sb` files and 
outputs a pure brainfuck string on stdout.

To use `sbc.py`:

1. Clone this repository
   - `git clone https://github.com/aanastasiou/springboard.git`

2. Create a new virtual environment
   - `virtualenv -p python3.9 pyenv/`

3. Activate the environment
   - `source pyenv/bin/activate`
   
4. Install dependencies
   - `pip install -r requirements.txt`

You are now ready to compile Springboard programs. Try `./sbc.py --help` for more information.

The compiler is "intelligent enough" to catch:
    - Cyclic imports
    - Cyclic definitions
    - Undefined symbols
    - Symbols being redefined
    
And optimises brainfuck code by removing redundant `><` and `+-` sequences of operations.


## Improvements (?)

- Allow complete/partial redefinition of a symbol:
  - `:` define symbol (if it already exists, throws error) 
  - `::` re-define symbol (if it already exists, the code it resolves to gets completely replaced, otherwise, throw undefined error)
  - `:=` extend symbol (if it already exists, the code it resolves to is extended, otherwise, throw undefined error)

- Capture the `main` of each program (that is, the "code section") as a separate symbol with a special name (e.g. `<filename>_main`)
  and allow it to be re-used. This can be useful if the stack has to be prepared in a specific way prior to executing a given program.


## Why Springboard?

The first implementation of what later became Springboard was, unsurprisingly, in Forth. Forth's 
ability to define a "vocabulary" of "words" that resolve to effects on the stack(s) results in 
very readable and clear code. Taken to the extreme, the actual Forth code itself, spells out the
solution to a given problem.

I was playing around with writing a stack based Brainfuck program. So, I launched `gforth` and started 
defining a vocabulary of words that resolved to Brainfuck strings. That is, one actually writes a Forth program
that literally spells out the equivalent Brainfuck program.  Here is that very first `gforth` program:

```
    : setzero ." [-] " ;
    : repnumber dup 0 = IF setzero ELSE DUP DUP SWAP ABS SWAP 0 < IF 45 ELSE 43 THEN swap 0 DO DUP EMIT LOOP THEN DROP ;
    : push repnumber  ." > " ;
    : pop ." <[-] " drop ;
    : swp ." <[->+>+<<]<[->+<]>>>[-<<<+>>>]<  " setzero swap ;
    : doub ." <[->+<]>[-<+>>+<]>[-<+>] " dup ;
    : add ." <[-<+>] " + ;
    : sub ." <[-<->] " - ;
    : mul ." < [->+>+<<] < [- > > [-<+>] > [-<+>>+<] > [-<+>] <<<<] > [-<+>] > [-] > [-] << " * ;

    2 push doub doub mul mul doub add 1 push sub 15 push sub
```

*This programs evaluates to 0*.

This worked, but:

1. It required a Forth interpreter, for that one ability to define and re-use symbols.
2. A given Forth interpreter has its own semantics and would require some effort to "lock down" 
   the remaining Forth around Springboard. For example:
   1. Notice what `repnumber` looks like. `repnumber` implements a substitution like `5 --> +++++`. 
   2. Similarly, `import` would become a separate function which, because of the way Forth works, would have to 
      expressed as ` ." somefile " import`.

This gave birth to `Springboard`. What you find at the bottom of a mechanical dish stack. 
