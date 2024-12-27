
# CFG Parser Implementations

This project implements a toolkit for working with Context-Free Grammars (CFGs), including FIRST and FOLLOW set calculation, a top-down (LL(1)) parser, and a bottom-up (SLR) parser. These tools are fundamental in compiler construction and formal language theory. The algorithms used are based on principles described in *Compilers: Principles, Techniques, and Tools (2nd Edition)* by Aho et al.

## Theoretical Background

A context-free grammar (CFG) is a formal grammar that defines a set of strings (a language). It consists of four components:

*   **N (Nonterminals):** A finite set of variables (e.g., A, B, S).
*   **Σ (Terminals):** A finite set of symbols that form the strings of the language (e.g., a, b, c).
*   **P (Productions):** A finite set of rules of the form A → α, where A ∈ N and α ∈ (N ∪ Σ)\*.
*   **S (Start Symbol):** A special nonterminal (S ∈ N) that initiates string generation.

**Chomsky Normal Form (CNF):** A CFG is in CNF if all productions are of the form A → BC or A → a.

# First & Follow Set Calculation

This section describes the implementation for calculating FIRST and FOLLOW sets, crucial for constructing parsing tables.

#### Assumptions for Input Grammars

*   'S' is always the initial symbol.
*   Nonterminals are uppercase letters.
*   Terminals are lowercase letters.
*   The empty string (ε) is represented by 'e'. 'e' is not a valid terminal.
*   '$' is not a valid terminal.
*   All nonterminals are productive.

### Input Format

Grammar rules are read from input.txt:

*   First line: Number of test cases (*n*).
*   For each test case:
    *   One line: Number of nonterminals (*m*).
    *   *m* lines: Production rules in the format <nonterminal> <derivations separated by spaces>.

**Example input.txt:**
```
2
2
S AS A
A a
2
S ASA
A a
```
### Output Format

For each test case, FIRST and FOLLOW sets are printed to the console:

First(Nonterminal) = {terminal1, terminal2, ...}
Follow(Nonterminal) = {terminal1, terminal2, ..., $} A blank line separates test case outputs.

**Example Output:**
```
First(S) = {a}
First(A) = {a}
Follow(S) = {$}
Follow(A) = {$, a}

First(S) = {a}
First(A) = {a}
Follow(S) = {$}
Follow(A) = {$, a}
```


# Top-Down (LL(1)) Parser

This section describes the table-driven predictive (LL(1)) parser implementation (Aho et al., Sections 4.4.3 and 4.4.4).

### Key Features

1.  LL(1) grammar verification.
2.  FIRST set calculation for strings.
3.  Parsing table construction (Algorithm 4.31).
4.  Table-driven predictive parsing (Algorithm 4.34).

### Input Format

*   **Grammar:** From `input.txt` (same format as First & Follow).
*   **Input String:** Passed to `analyze_string` (space-separated tokens).

**Example Grammar in `input.txt`:**
```
E TE'
E' +TE' e
T FT'
T' *FT' e
F (E) id
```


### Example Usage:

```python
# ... (Code to read grammar and create First_Follow object)
FF.analyze_string("id + id * id")

```
### Output Format
analyze_string prints a step-by-step parsing trace (stack and remaining input) and indicates acceptance or rejection.

### Example Output (abbreviated):
```
Analizando la cadena de entrada: 'id + id * id'

Análisis paso a paso:
Pila: ['$', 'E'], Entrada: id + id * id $
...
La cadena de entrada fue aceptada.
```
# Bottom-Up (SLR) Parser
This section describes the SLR parser implementation (Aho et al., Sections 4.5 and 4.6).

Key Features
CLOSURE(I) calculation (Section 4.6.2).
LR(0) collection construction (Section 4.6.2).
SLR parsing table construction (Algorithm 4.46).
LR parsing algorithm (Algorithm 4.44).
Input Format
Grammar rules are read from input.txt:

Each line: Nonterminal -> Production1 | Production2 | ...

### Example input.txt:
```
S' -> S
S -> S + T | T
T -> T * F | F
F -> ( S ) | id
```
Input strings are passed to LRparser.

### Example Usage:

```Python

grammar_rules = read_grammar()
ACTION, GOTO = SLRTable(grammar_rules)
LRparser("id + id * id", ACTION, GOTO)
```
### Output Format
LRparser prints a step-by-step parsing trace (stack, input, action) and indicates acceptance or rejection.

### Example Output (abbreviated):
```
Step-by-step analysis:

Stack: [0], Input: ['id', '+', 'id', '*', 'id', '$'], Current symbol: id
Shift: 'id' -> State 5
...
String accepted. Final stack: [0, 'S', 1]
```
# References
Aho, Alfred V. et al. Compilers: Principles, Techniques, and Tools (2nd Edition). USA: Addison-Wesley Longman Publishing Co., Inc., 2006. ISBN: 0321486811.

# Developers  
- **[Juan Pablo Corena Alvarez]**
- **[Pablo Cabrejos Múnera]**
- **[Martin Vanegas Ospina]**
  
Thank you for your hard work!!!
