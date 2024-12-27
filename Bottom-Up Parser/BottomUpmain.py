# Function to find the follow sets of each nonterminal
def compute_follow(grammar):

    follow = {key: set() for key in grammar}  # 'follow' dictionary initialized with nonterminals as keys
    start_symbol = list(grammar.keys())[0]  # Start symbol is the first nonterminal in the grammar
    follow[start_symbol].add('$')  # The FOLLOW set of the start symbol includes the end-of-input symbol '$'

    changed = True
    while changed:  # Continue until no changes are made
        changed = False
        for alpha, productions in grammar.items():  # Iterate through each nonterminal and its production rules
            for A in productions:  # Iterate through each production of the nonterminal
                for i, symbol in enumerate(A):
                    if symbol in grammar:  # If the symbol is a nonterminal (needs a FOLLOW set)
                        rest = A[i + 1:]  # Get the rest of the production after the current symbol
                        follow_set = {x for x in rest if x not in grammar}  # Collect terminals from the rest of A

                        # If the current symbol is the last one in the production
                        if not rest or all(x in grammar for x in rest):
                            follow_set |= follow[alpha]  # Add FOLLOW of alpha to the FOLLOW set of the nonterminal

                        # If the FOLLOW set of the nonterminal has changed, update and set 'changed' to True
                        if follow_set - follow[symbol]:
                            follow[symbol].update(follow_set)
                            changed = True
    return follow

#Function to Read any LR arbitrary augmented grammar
def read_grammar():
    grammar_rules = {} # dict with key = Nonterminals and values = productions
    with open("input.txt") as file:
        lines = file.readlines() # read the lines of the .txt
        for line in lines:
            line = line.strip() #remove whitespaces if found
            if not line:
                continue
            if '->' in line:  # Only process lines with "->"
                left_side, right_side = line.split("->") # Split right and left side of production
                left_side = left_side.strip()
                productions = [tuple(prod.strip().split()) for prod in right_side.split('|')] # Save all productions in a list
                grammar_rules[left_side] = productions # Save productions as values of the dict with key = NonTerminals
            else:
                print(f"Warning: line does not match pretended format: {line}")
    return grammar_rules

# Closure Function for finding LR(0) Automaton States. Follows this two rules
# Add every item in I to CLOSURE(I)
# If A → α‧B β is in CLOSURE(I) and B → γ is a production, then add B → ‧γ to CLOSURE(I), if it is not already there
#Involves the productions that have the dot right before the non-terminal symbol.
# This step helps us identify all the possible items that can be derived from the current set.
def Closure(I, grammar):
    closure = set(I)
    added = True
    while added:
        added = False
        new_items = set()
        for item in closure:
            # Assuming each item is a tuple like (A, α, Bβ) where B is a non-terminal
            A, alpha, beta = item  # Destructure the item
            if beta:  # If there's something after the dot
                B = beta[0]  # First symbol after the dot
                if B in grammar:  # Check if B is a non-terminal with productions
                    for production in grammar[B]:
                        new_item = (B, tuple(), production)  # Form the new item B -> .γ
                        if new_item not in closure:
                            new_items.add(new_item)
                            added = True
        closure.update(new_items)  # Add all new items found in this iteration

    return closure

#GOTO Function for finding the transitions of the LR(0) automaton (next state after each reduction)
# GOTO(I,X) is the Closure of all items A → αX.β such as A → α‧Xβ is in I
#In simple words: Determines the next set of items by shifting the dot one position to the right
def GOTO(I, X, grammar):
    goto = set()
    for item in I:
        A, alpha, beta = item  # Destructure the item
        if beta and beta[0] == X:  # Check if X is the first symbol in beta
            # Move the dot over X by creating a new item
            new_alpha = alpha + (X,)
            new_beta = beta[1:]
            new_item = (A, new_alpha, new_beta)
            goto.add(new_item)

    # Compute the closure of the resulting items
    return Closure(goto, grammar)

#Find the Collection of sets of LR(0) items
def LRcollection(grammar):
    # Initialize C with the closure of the augmented start symbol S'
    start_symbol = list(grammar.keys())[0]  # The augmented start symbol
    start_value = grammar[start_symbol][0]  # Use the first production of the start symbol 
    initial_item = (start_symbol, tuple(), start_value)  # S' -> .S
    C = [Closure({initial_item}, grammar)]  # Start with the closure of {S' -> .S}

    added = True
    while added:
        added = False
        new_states = []  # To keep track of new sets to add to C

        # For each set of items I in C
        for I in C:
            # For each grammar symbol X (terminals and non-terminals)
            for X in set(symbol for rules in grammar.values() for rule in rules for symbol in rule):
                goto_result = GOTO(I, X, grammar)

                # Only add if GOTO(I, X) is not empty and not already in C
                if goto_result and goto_result not in C and goto_result not in new_states:
                    new_states.append(goto_result)
                    added = True

        # Add any new states found in this iteration
        C.extend(new_states)

    return C

#Print the canonical Collection
def PrintCollection(C):
    for i, state in enumerate(C):
        print(f"I{i}:")
        for item in sorted(state):
            A, alpha, beta = item
            # if beta exists, dot is placed between alpha y beta
            if beta:
                alphaBeta = f"{' '.join(alpha)} . {' '.join(beta)}"
            else:
                # if beta is empty, dot is placed at the end of alpha
                alphaBeta = f"{' '.join(alpha)} ."

            # Prints the production with the dot
            print(f"  {A} -> {alphaBeta}")

#SLR TABLE for analyzing grammar syntax
def SLRTable(grammar):
    ACTION = {}  # Dictionary to store ACTION table (shift, reduce, accept)
    GOTO_Table = {}  # Dictionary to store GOTO table (next state transitions for nonterminals)

    # Compute the FOLLOW set for all nonterminals
    FollowSet = compute_follow(grammar)

    # Generate the collection of LR items for the LR analysis (creates sets of items)
    C = LRcollection(grammar)

    # Iterate over all the item sets in C
    for i, I in enumerate(C):
        for item in I:
            A, alpha, beta = item  # Decompose the item into production: A -> α . β

            symbol = beta[0] if beta else None  # If beta is empty, there is no symbol to analyze

            # If symbol is a terminal (or special symbols like '+', '*', etc.), shift action
            if symbol and (symbol.islower() or symbol in {'+', '*', 'id', '(', ')', '/', '-'}):
                j = None
                for k, J in enumerate(C):
                    # GOTO function determines the next set of items after reading a terminal
                    new_set = GOTO(I, symbol, grammar)
                    if new_set == J:
                        j = k  # Found the next state
                        break
                if j is not None:
                    # Add the shift action to the ACTION table
                    ACTION[(i, symbol)] = ('shift', j)

            # If the dot is at the end of the production (indicating a reduction)
            elif len(beta) == 0:
                if A == list(grammar.keys())[0]:  # If it's the start symbol, it's an acceptance action
                    ACTION[(i, '$')] = ('accept',)
                else:  # Otherwise, reduce using the production corresponding to A -> α
                    for term in FollowSet[A]:
                        # For each terminal in the FOLLOW set of A, add a reduction action
                        ACTION[(i, term)] = ('reduce', A, alpha)

        # Iterate over all nonterminals in the grammar to fill the GOTO table
        for X in grammar:
            j = None
            for k, J in enumerate(C):
                # GOTO function determines the next set of items after reading a nonterminal
                new_set = GOTO(I, X, grammar)
                if new_set == J:
                    j = k  # Found the next state for the nonterminal
                    break
            if j is not None:
                # Add the GOTO transition for the nonterminal to the GOTO table
                GOTO_Table[(i, X)] = j

    # Return the populated ACTION and GOTO tables
    return ACTION, GOTO_Table

#Print ACTION and GOTO table in desired format
def print_SLR_table(ACTION, GOTO):
    print("ACTION Table:")
    print("{:<10} {:<10} {:<15}".format("State", "Symbol", "Action"))
    for (state, symbol), action in sorted(ACTION.items()):
        action_type = action[0]
        if action_type == 'shift':
            print("{:<10} {:<10} {:<15}".format(state, symbol, f"shift {action[1]}"))
        elif action_type == 'reduce':
            print("{:<10} {:<10} {:<15}".format(state, symbol, f"reduce {action[1]} -> {action[2]}"))
        elif action_type == 'accept':
            print("{:<10} {:<10} {:<15}".format(state, symbol, "accept"))

    print("\nGOTO Table:")
    print("{:<10}{:<10}  {:<15}".format("State", "Non-Terminal", "Goto State"))
    for (state, non_terminal), next_state in sorted(GOTO.items()):
        print("{:<10} {:<10}  {:<15}".format(state, non_terminal, next_state))

#LR Parser for accepting or rejecting a w string in a grammar
#Analyzes input text from left to right to produce a rightmost derivation in reverse
def LRparser(w, ACTION, GOTO):
    stack = [0]  # The stack starts with state 0 (initial state)
    w = w.split() + ["$"]  # Split the input string into tokens and add the end-of-input symbol '$'
    idx = 0  # Index to iterate over the input tokens
    a = w[idx]  # The first token in the input string

    print("Step-by-step analysis:")

    while True:
        s = stack[-1]  # The current state is the last element in the stack
        print(f"\nStack: {stack}, Input: {w[idx:]}, Current symbol: {a}")

        # Check which action to take based on the current state and input symbol
        action = ACTION.get((s, a))

        if action is None:
            # If no action is found, it means there's an error in the parsing process
            print("Error: No action found. The string is not accepted.")
            return False

        if action[0] == "shift":
            # If the action is "shift", push the current token and the new state onto the stack
            print(f"Shift: '{a}' -> State {action[1]}")
            stack.append(a)  # Push the token onto the stack
            stack.append(action[1])  # Push the new state onto the stack
            idx += 1  # Move to the next token in the input
            a = w[idx] if idx < len(w) else "$"  # If no more input, set the symbol to the end-of-input '$'

        elif action[0] == "reduce":
            # If the action is "reduce", apply the corresponding production rule
            A, beta = action[1], action[2]
            len_beta = len(beta)

            print(f"Reduce using {A} -> {' '.join(beta)}")

            # Pop 2 * len(beta) elements from the stack (removing the symbols and states)
            for _ in range(2 * len_beta):
                stack.pop()

            # Get the state after the reduction
            state = stack[-1]
            new_state = GOTO.get((state, A))  # Look up the next state in the GOTO table

            if new_state is None:
                # If no valid GOTO state is found, there's an error
                print(f"Error: No GOTO found for {A} in state {state}.")
                return False

            # Push the nonterminal A and the new state onto the stack
            stack.append(A)
            stack.append(new_state)  # Add the new state for the nonterminal A
            print(f"GOTO: Move to state {new_state} after reduction")

        elif action[0] == "accept":
            # If the action is "accept", the input is successfully parsed
            print(f"String accepted. Final stack: {stack}")
            return True


def main():
    # Read the grammar rules from a file or input
    grammar_rules = read_grammar()
    print("Loaded grammar:", grammar_rules)

    # Generate the LR(0) item collection for the grammar
    C = LRcollection(grammar_rules)
    print("LR(0) Canonical Collection")
    PrintCollection(C)

    # Generate the ACTION and GOTO tables based on the grammar
    ACTION, GOTO = SLRTable(grammar_rules)
    print("SLR TABLE")
    print_SLR_table(ACTION, GOTO)

    # Ask the user to input a string for parsing
    w = input("\nEnter the string to analyze: ")
    LRparser(w, ACTION, GOTO)


if __name__ == "__main__":
    main()
