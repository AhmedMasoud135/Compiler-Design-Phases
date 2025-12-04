from typing import Dict, Set, List
from grammar_parser import Grammar


def compute_first_sets(grammar: Grammar) -> Dict[str, Set[str]]:

    first = {}
    
    # Initialize FIRST sets
    for terminal in grammar.terminals:
        first[terminal] = {terminal}
    
    for nonterminal in grammar.nonterminals:
        first[nonterminal] = set()
    
    first['ε'] = {'ε'}
    
    # Iterate until no changes
    changed = True
    while changed:
        changed = False
        
        for nt, productions in grammar.productions.items():
            for prod in productions:
                old_size = len(first[nt])
                
                if not prod:  # ε production
                    first[nt].add('ε')
                else:
                    # Add FIRST of production
                    first[nt] |= first_of_sequence(prod, first)
                
                if len(first[nt]) > old_size:
                    changed = True
    
    return first


def first_of_sequence(symbols: List[str], first_sets: Dict[str, Set[str]]) -> Set[str]:

    result = set()
    
    for symbol in symbols:
        symbol_first = first_sets.get(symbol, {symbol})
        result |= symbol_first - {'ε'}
        
        if 'ε' not in symbol_first:
            return result
    
    # All symbols can derive ε
    result.add('ε')
    return result


def compute_follow_sets(grammar: Grammar, first_sets: Dict[str, Set[str]]) -> Dict[str, Set[str]]:
    
    # Initialize FOLLOW sets
    follow = {nt: set() for nt in grammar.nonterminals}
    follow[grammar.start_symbol].add('$')
    
    # Iterate until no changes
    changed = True
    while changed:
        changed = False
        
        for nt, productions in grammar.productions.items():
            for prod in productions:
                for i, symbol in enumerate(prod):
                    if not grammar.is_nonterminal(symbol):
                        continue
                    
                    old_size = len(follow[symbol])
                    
                    # Rest of production
                    rest = prod[i + 1:]
                    
                    if not rest:
                        # A -> αB, add FOLLOW(A) to FOLLOW(B)
                        follow[symbol] |= follow[nt]
                    else:
                        # A -> αBβ
                        first_rest = first_of_sequence(rest, first_sets)
                        follow[symbol] |= first_rest - {'ε'}
                        
                        if 'ε' in first_rest:
                            # β can derive ε, add FOLLOW(A) to FOLLOW(B)
                            follow[symbol] |= follow[nt]
                    
                    if len(follow[symbol]) > old_size:
                        changed = True
    
    return follow
