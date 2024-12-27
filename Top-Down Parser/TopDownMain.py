from collections import defaultdict

# Clase para calcular conjuntos First, Follow y la tabla de análisis
class First_Follow:
    def __init__(self, productions):
        self.productions = productions
        self.firstSet = defaultdict(set)
        self.followSet = defaultdict(set)
        self.parsingTable = defaultdict(dict)

    def add_first(self, nonT, firstSet):
        self.firstSet[nonT].update(firstSet)

    def add_follow(self, nonT, followSet):
        self.followSet[nonT].update(followSet)

    def aux_first(self, derivation, first_set, visited=None):
        if visited is None:
            visited = set()
        if not derivation:
            first_set.add("e")
            return

        first_s1 = derivation[0]
        if first_s1 in visited:
            return
        visited.add(first_s1)

        for deriv in self.productions.get(first_s1, []):
            if deriv == first_s1:
                continue
            first_s2 = deriv[0]
            if first_s2 == "e":
                self.aux_first(derivation[1:], first_set, visited)
            elif first_s2.isupper():
                self.aux_first(deriv, first_set, visited)
            else:
                first_set.add(first_s2)

        visited.remove(first_s1)

    def exploreFirst(self, derivation):
        if derivation == ("e",):
            return {"e"}
        first_set = set()
        first_symbol = derivation[0]
        if first_symbol.isupper():
            self.aux_first(derivation, first_set)
        else:
            first_set.add(first_symbol)
        return first_set

    def exploreFollow(self, nonT, follow_set, visited=None):
        if visited is None:
            visited = set()
        if nonT == list(self.productions.keys())[0]:
            follow_set.add("$")
        for nonTerm, derivations in self.productions.items():
            for production in derivations:
                pos = production.index(nonT) if nonT in production else -1
                while pos != -1:
                    nextTo = pos + 1
                    if nextTo < len(production):
                        next_symbol = production[nextTo]
                        if next_symbol.isupper():
                            follow_set.update(self.firstSet[next_symbol] - {"e"})
                            if "e" in self.firstSet[next_symbol]:
                                self.exploreFollow(nonTerm, follow_set, visited)
                        else:
                            follow_set.add(next_symbol)
                    else:
                        if nonT != nonTerm:
                            self.exploreFollow(nonTerm, follow_set, visited)
                    pos = production.index(nonT, pos + 1) if nonT in production[pos + 1:] else -1

    def compute_first(self):
        for nonTerminal, derivations in self.productions.items():
            first_set = set()
            for derivation in derivations:
                first_set.update(self.exploreFirst(derivation))
            self.add_first(nonTerminal, first_set)

    def compute_follow(self):
        for nonTerminal in self.productions.keys():
            self.exploreFollow(nonTerminal, self.followSet[nonTerminal])

    def is_LL1(self):
        """
        Verifica si la gramática es LL(1) o no.
        Devuelve True si la gramática es LL(1), False en caso contrario.
        """
        for nonTerminal, derivations in self.productions.items():
            # Comprobamos las entradas de la tabla de análisis para cada no terminal
            entries = {}
            for derivation in derivations:
                first_set = self.exploreFirst(derivation)
                if "e" in first_set:  # Si hay épsilon en First(derivación), agregamos Follow al análisis
                    first_set = (first_set - {"e"}).union(self.followSet[nonTerminal])
                # Verificamos que no haya conflictos en la tabla de análisis para esta producción
                for terminal in first_set:
                    if terminal in entries:
                        print(f"Conflicto encontrado en {nonTerminal}, {terminal}: "
                              f"{entries[terminal]} y {derivation}")
                        return False
                    entries[terminal] = derivation
        print("La gramática es LL(1)")
        return True

    def compute_parsing_table(self):
        for nonTerminal, derivations in self.productions.items():
            for derivation in derivations:
                first_of_derivation = self.exploreFirst(derivation)
                for terminal in first_of_derivation - {"e"}:
                    self.parsingTable[nonTerminal][terminal] = derivation
                if "e" in first_of_derivation:
                    for terminal in self.followSet[nonTerminal]:
                        self.parsingTable[nonTerminal][terminal] = derivation

    def print_parsing_table(self):
        print("Tabla de análisis (Parsing Table):")
        for nonTerminal, row in self.parsingTable.items():
            for terminal, production in row.items():
                print(f"{nonTerminal}, {terminal} -> {production}")

    def parse_step(self, stack, tokens, index):
        # Verificar si la pila está vacía
        if not stack:
            print("Análisis finalizado.")
            return True, index

        # Sacar el símbolo superior de la pila
        top = stack.pop()
        current_token = tokens[index] if index < len(tokens) else '$'  # El token actual de la entrada

        print(f"Pila: {stack}, Entrada: {' '.join(tokens[index:])}")

        # Si el símbolo en la pila es un terminal y coincide con el token actual
        if top == current_token:
            print(f"Coinciden '{top}', avanzando en la entrada.")
            index += 1  # Avanzamos en la entrada
            return self.parse_step(stack, tokens, index)  # Recursión para procesar el siguiente token

        # Si es un no terminal, obtener la producción desde la tabla de análisis
        elif top in self.parsingTable and current_token in self.parsingTable[top]:
            production = self.parsingTable[top][current_token]
            print(f"Aplicando producción: {top} -> {' '.join(production)}")
            # Desapilar el no terminal y agregar la producción a la pila
            if production != ("e",):  # Si no es una producción épsilon
                stack.extend(reversed(production))
            return self.parse_step(stack, tokens, index)  # Recursión para procesar el siguiente token

        # Si no se puede aplicar ninguna producción, hay un error
        else:
            print(f"Error: no hay producción para {top} con '{current_token}'")
            return False, index

    def analyze_string(self, input_string):
        # Convertir la cadena en tokens con espacios entre cada token
        tokens = []
        i = 0
        while i < len(input_string):
            if input_string[i:i + 2] == 'id':
                tokens.append('id')
                i += 2
            elif input_string[i] in '+*()':
                tokens.append(input_string[i])
                i += 1
            else:
                i += 1  # Ignorar espacios o caracteres no reconocidos

        tokens.append('$')  # Añadir símbolo de fin de cadena
        print(f"\nAnalizando la cadena de entrada: '{input_string}'")

        # Inicializar la pila con el símbolo inicial y el símbolo de fin de cadena
        stack = ["$", list(self.productions.keys())[0]]  # Comienza con $ y el símbolo inicial
        index = 0

        print("\nAnálisis paso a paso:")

        while len(stack) > 0:
            top = stack[-1]
            current_input = tokens[index]
            print(f"Pila: {stack}, Entrada: {' '.join(tokens[index:])}")

            # Si solo queda '$' en la pila y en la entrada, la cadena fue aceptada
            if top == "$" and current_input == "$":
                print("La cadena de entrada fue aceptada.")
                return

            # Si el token de entrada actual coincide con el tope de la pila
            if top == current_input:
                print(f"Coinciden '{top}', avanzando en la entrada.")
                stack.pop()
                index += 1

            # Si el tope de la pila es un no terminal, buscamos la producción en la tabla
            elif top in self.parsingTable and current_input in self.parsingTable[top]:
                production = self.parsingTable[top][current_input]
                print(f"Aplicando producción: {top} -> {' '.join(production)}")
                stack.pop()

                if production != ("e",):  # Si no es una producción épsilon
                    for symbol in reversed(production):  # Invertir el orden de los símbolos
                        stack.append(symbol)

            # Si no hay coincidencia en la tabla de análisis, no hay producción válida
            else:
                print(f"Error: no hay producción para {top} con '{current_input}'")
                return

        # Si el ciclo se completa sin que ambos símbolos sean `$`, la cadena no fue aceptada
        print("La cadena de entrada no fue aceptada.")


# Función principal para ejecutar el análisis
def main():
    # Ejemplo de gramática cargada manualmente
    grammar = {
        'E': [('T', "E'")],
        "E'": [('+', 'T', "E'"), ('e',)],  
        'T': [('F', "T'")],
        "T'": [('*', 'F', "T'"), ('e',)],
        'F': [('(', 'E', ')'), ('id',)]
    }

    print("Gramática cargada:", grammar)

    # Crear objeto para manejar First y Follow
    FF = First_Follow(grammar)

    # Calcular conjuntos First y Follow
    FF.compute_first()
    FF.compute_follow()

    # Calcular tabla de análisis
    FF.compute_parsing_table()

    # Imprimir los resultados
    print("Conjuntos First:")
    for nonT, first_set in FF.firstSet.items():
        print(f"First({nonT}) = {first_set}")

    print("Conjuntos Follow:")
    for nonT, follow_set in FF.followSet.items():
        print(f"Follow({nonT}) = {follow_set}")

    # Imprimir tabla de análisis
    FF.print_parsing_table()

    if FF.is_LL1():
        print()
    else:
        print("La gramática no es LL(1)")

    # Analizar cadena de entrada
    FF.analyze_string("id + id * id")

# Ejecutar el código principal
if __name__ == '__main__':
    main()
