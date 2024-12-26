class First_Follow:
    def __init__(self, productions):
        self.productions = productions
        self.firstSet = {}
        self.followSet = {}

    # Add to the first dict a non-terminal (key) and a first set (firstSet)
    def add_first(self, nonT, firstSet):
        self.firstSet[nonT] = deleteDuplicates(firstSet)

    # Add to the follow dict a non-terminal (key) and a follow set (followSet)
    def add_follow(self, nonT, followSet):
        self.followSet[nonT] = deleteDuplicates(followSet)

    # Recursive function to calculate the first set
    # for a given derivation ABC where S -> ABC
    def aux_first(self, derivation, set):

        # if all non-terminals in a derivation produce epsilon
        # then add epsilon to S where S -> ABC
        if not derivation:
            return set.append("e")

        first_s1 = derivation[0]

        # Iterate over the derivations of the first symbol
        for deriv in self.productions[first_s1]:

            # Skip this iteration if the derivation is
            # equal to the first symbol
            if deriv == first_s1:
                continue

            first_s2 = deriv[0]

            # Find the first set of the next non-terminal
            if first_s2 == "e":
                self.aux_first(derivation[1:], set)

            # Find the first set of the first non-terminal
            elif first_s2.isupper():
                self.aux_first(deriv, set)

            # Add the terminal symbol to the set
            else:
                set.append(first_s2)

        return set

    # Initial function to calculate the first set
    # for a given derivation
    def exploreFirst(self, derivation):
        if derivation == "e":
            return [derivation]

        first_symbol = derivation[0]

        # Call the recursive function if the first
        # symbol is a non-terminal
        if first_symbol.isupper():
            return self.aux_first(derivation, [])

        # Return the terminal symbol
        else:
            return [first_symbol]

    # Recursive function to calculate the follow set
    # for a given non-terminal
    def exploreFollow(self, nonT, set):

        # Add $ to the initial non-terminal
        if nonT == "S":
            set.append("$")

        # Iterate over all the productions of the CFG
        for nonTerm, derivations in self.productions.items():
            for derivation in derivations:

                # Check if nonT is in this derivation
                if derivation.find(nonT) == -1:
                    continue

                nextTo = derivation.find(nonT) + 1

                # Check if there is a symbol next to nonT
                if nextTo < len(derivation):
                    next = derivation[nextTo]

                    if next.isupper():
                        # Add the first set of the next symbol to this follow set
                        for i in self.firstSet[next]:
                            if i != "e":
                                set.append(i)

                        # Add the follow set of the nonTerm to this follow set
                        if "e" in self.firstSet[next]:

                            # Skip this iteration if nonT is equal
                            # to the current non-terminal
                            if nonT == nonTerm:
                                continue
                            self.exploreFollow(nonTerm, set)

                    # Add the terminal symbol to the follow set
                    else:
                        set.append(next)

                else:
                    if nonT == nonTerm:
                        continue
                    self.exploreFollow(nonTerm, set)

        return set

# Delete repeated elements across a given list
def deleteDuplicates(list):
    new_list = []
    for n in list:
        if n not in new_list:
            new_list.append(n)
    return new_list

def main():
    # Read the input.txt file
    with open("input.txt") as input:

        # Read the number of cases
        cases = int(input.readline().strip())

        while 0 < cases:

            # Read the number of nonterminals
            k = input.readline().strip()
            k = int(k)

            # Dictionary where the key is the nonterminal and the value is a
            # list of the derivations alternatives for each production
            productions = {}

            # Read and store the productions
            while 0 < k:
                production = input.readline().strip().split()
                key = production.pop(0)
                productions[key] = production
                k -= 1

            FF = First_Follow(productions)

            # Find the first sets for each non-terminal
            for nonTerminal in productions.keys():
                firstNonT = []
                derivations = productions[nonTerminal]

                for derivation in derivations:
                    first = FF.exploreFirst(derivation)
                    for i in first:
                        firstNonT.append(i)

                FF.add_first(nonTerminal, firstNonT)

            # Find the follow sets for each non-terminal
            for nonTerminal in productions.keys():
                followNonT = []
                follow = FF.exploreFollow(nonTerminal, [])
                for i in follow:
                    followNonT.append(i)

                FF.add_follow(nonTerminal, followNonT)

            # Print the results for this CFG
            for nonT, set in FF.firstSet.items():
                set_string = ""
                set_string += set[0]
                for s in set[1:]:
                    set_string += ", " + s

                print(f"First({nonT}) = " + "{" + f"{set_string}" + "}")

            for nonT, set in FF.followSet.items():
                set_string = ""
                set_string += set[0]
                for s in set[1:]:
                    set_string += ", " + s

                print(f"Follow({nonT}) = " + "{" + f"{set_string}" + "}")

            print()
            cases -= 1

    input.close()

if __name__ == "__main__":
   main()