from typing import Dict, List, Set
from grammar_parser import Grammar
import copy


def remove_left_recursion(grammar: Grammar) -> Grammar:
   
    productions = copy.deepcopy(grammar.productions)
    nonterminals = list(productions.keys())
    
    # Process each nonterminal
    for i, Ai in enumerate(nonterminals):
        # Eliminate indirect left recursion
        for j in range(i):
            Aj = nonterminals[j]
            new_prods = []
            
            for prod in productions[Ai]:
                if prod and prod[0] == Aj:
                    for aj_prod in productions[Aj]:
                        new_prods.append(aj_prod + prod[1:])
                else:
                    new_prods.append(prod)
            
            productions[Ai] = new_prods
        
        # Eliminate immediate left recursion
        productions = eliminate_immediate_left_recursion(productions, Ai)
    
    return Grammar(productions, grammar.start_symbol)


def eliminate_immediate_left_recursion(productions: Dict[str, List[List[str]]], 
                                      nonterminal: str) -> Dict[str, List[List[str]]]:
    
    prods = productions[nonterminal]
    recursive = []  # Productions with left recursion (A -> A α)
    non_recursive = []  # Productions without left recursion (A -> β)
    
    for prod in prods:
        if prod and prod[0] == nonterminal:
            recursive.append(prod[1:])  # α part
        else:
            non_recursive.append(prod)
    
    # If no left recursion, return unchanged
    if not recursive:
        return productions
    
    # Create new nonterminal A'
    new_nt = nonterminal + "'"
    while new_nt in productions:
        new_nt += "'"
    
    new_prods_a = []
    for prod in non_recursive:
        new_prods_a.append(prod + [new_nt])
    
    if not new_prods_a:  # If all productions were recursive
        new_prods_a = [[new_nt]]
    
    new_prods_a_prime = []
    for prod in recursive:
        new_prods_a_prime.append(prod + [new_nt])
    new_prods_a_prime.append([])  # ε production
    
    productions[nonterminal] = new_prods_a
    productions[new_nt] = new_prods_a_prime
    
    return productions


def left_factor(grammar: Grammar) -> Grammar:
    
    productions = copy.deepcopy(grammar.productions)
    changed = True
    
    while changed:
        changed = False
        for nt in list(productions.keys()):
            prods = productions[nt]
            
            # Find common prefixes
            prefixes = find_common_prefixes(prods)
            
            if prefixes:
                changed = True
                # Factor out the longest common prefix
                prefix, indices = max(prefixes.items(), key=lambda x: len(x[0]))
                
                # Create new nonterminal
                new_nt = nt + "'"
                while new_nt in productions:
                    new_nt += "'"
                
                # Split productions
                factored_prods = []  # Productions with common prefix removed
                other_prods = []     # Productions without the prefix
                
                for i, prod in enumerate(prods):
                    if i in indices:
                        suffix = prod[len(prefix):]
                        factored_prods.append(suffix if suffix else [])
                    else:
                        other_prods.append(prod)
                
                # Update productions
                productions[nt] = other_prods + [list(prefix) + [new_nt]]
                productions[new_nt] = factored_prods
                break
    
    return Grammar(productions, grammar.start_symbol)


def find_common_prefixes(productions: List[List[str]]) -> Dict[tuple, Set[int]]:

    prefixes = {}
    
    for i in range(len(productions)):
        for j in range(i + 1, len(productions)):
            prod_i = productions[i]
            prod_j = productions[j]
            
            # Find common prefix
            k = 0
            while k < len(prod_i) and k < len(prod_j) and prod_i[k] == prod_j[k]:
                k += 1
            
            if k > 0:  # Found common prefix
                prefix = tuple(prod_i[:k])
                if prefix not in prefixes:
                    prefixes[prefix] = {i, j}
                else:
                    prefixes[prefix].add(i)
                    prefixes[prefix].add(j)
    
    return prefixes


def needs_transformation_for_ll1(grammar: Grammar) -> bool:
    
    # Check for left recursion
    for nt, prods in grammar.productions.items():
        for prod in prods:
            if prod and prod[0] == nt:
                return True
    
    # Check for left factoring needed
    for prods in grammar.productions.values():
        if find_common_prefixes(prods):
            return True
    
    return False
