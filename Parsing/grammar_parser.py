import re
from typing import Dict, List, Set, Tuple


class Grammar:    
    def __init__(self, productions: Dict[str, List[List[str]]], start_symbol: str = None):
        
        self.productions = productions
        self.start_symbol = start_symbol or list(productions.keys())[0]
        self.nonterminals = set(productions.keys())         # Nonterminals are Keys of the dictionary
        self.terminals = self._compute_terminals()
        
    def _compute_terminals(self) -> Set[str]:               # terminals are symbols that are not nonterminals
        terminals = set()
        for prods in self.productions.values():
            for prod in prods:
                for symbol in prod:
                    if symbol not in self.nonterminals and symbol != 'ε':
                        terminals.add(symbol)
        terminals.add('$')  
        return terminals
    
    def is_terminal(self, symbol: str) -> bool:
        return symbol in self.terminals or symbol == 'ε'
    
    def is_nonterminal(self, symbol: str) -> bool:
        return symbol in self.nonterminals
    
    def __str__(self) -> str:
        lines = []
        for nt, prods in self.productions.items():
            rhs = ' | '.join([' '.join(p) if p else 'ε' for p in prods])
            lines.append(f"{nt} -> {rhs}")
        return '\n'.join(lines)


def parse_grammar(text: str) -> Grammar:
    """
    Parse grammar from text format.
    
    Expected format:
        E -> T + E | T
        T -> int | ( E )
    """
    productions = {}
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
    
    for line in lines:
        if '->' not in line:
            raise ValueError(f"Invalid production: {line}")
        
        lhs, rhs = line.split('->', 1)
        lhs = lhs.strip()
        
        if not lhs:
            raise ValueError("Empty left-hand side in production")
        
        # Parse alternatives
        alternatives = [alt.strip() for alt in rhs.split('|')]
        prod_bodies = []
        
        for alt in alternatives:
            if not alt or alt == 'ε':
                prod_bodies.append([])  # Epsilon production
            else:
                # Tokenize the production body
                tokens = tokenize_production(alt)
                prod_bodies.append(tokens)
        
        if lhs in productions:
            productions[lhs].extend(prod_bodies)
        else:
            productions[lhs] = prod_bodies
    
    if not productions:
        raise ValueError("Empty grammar")
    
    return Grammar(productions)


def tokenize_production(text: str) -> List[str]:

    tokens = []
    i = 0
    text = text.strip()
    
    while i < len(text):
        if text[i].isspace():
            i += 1
            continue
        
        # Multi-character identifiers (alphanumeric + underscore)
        if text[i].isalnum() or text[i] == '_':
            j = i
            while j < len(text) and (text[j].isalnum() or text[j] == '_'):
                j += 1
            tokens.append(text[i:j])
            i = j
        # Single character operators/delimiters
        else:
            tokens.append(text[i])
            i += 1
    
    return tokens


def validate_grammar(grammar: Grammar) -> Tuple[bool, List[str]]:
    
    issues = []
    
    # Check for undefined nonterminals
    for nt, prods in grammar.productions.items():
        for prod in prods:
            for symbol in prod:
                if symbol.isupper() and symbol not in grammar.nonterminals:
                    if not grammar.is_terminal(symbol):
                        issues.append(f"Warning: '{symbol}' used in production but not defined")
    
    # Check for unreachable nonterminals
    reachable = {grammar.start_symbol}
    changed = True
    while changed:
        changed = False
        for nt in list(reachable):
            for prod in grammar.productions.get(nt, []):
                for symbol in prod:
                    if symbol in grammar.nonterminals and symbol not in reachable:
                        reachable.add(symbol)
                        changed = True
    
    unreachable = grammar.nonterminals - reachable
    if unreachable:
        issues.append(f"Warning: Unreachable nonterminals: {unreachable}")
    
    return len(issues) == 0 or all('Warning' in i for i in issues), issues


# Default grammar
DEFAULT_GRAMMAR = """E -> T + E | T
T -> T * int | int | ( E )"""
