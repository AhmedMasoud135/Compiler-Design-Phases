from typing import Dict, List, Tuple, Set, Optional
from grammar_parser import Grammar
from first_follow import compute_first_sets, compute_follow_sets, first_of_sequence


class LL1Parser:    
    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.first_sets = compute_first_sets(grammar)
        self.follow_sets = compute_follow_sets(grammar, self.first_sets)
        self.parsing_table = self._build_parsing_table()
        self.conflicts = self._detect_conflicts()
    
    def _build_parsing_table(self) -> Dict[Tuple[str, str], List[str]]:

        table = {}
        
        for nt, productions in self.grammar.productions.items():
            for prod in productions:
                # Compute FIRST of production
                first_prod = first_of_sequence(prod if prod else [], self.first_sets)
                
                # For each terminal in FIRST(prod), add entry
                for terminal in first_prod - {'ε'}:
                    key = (nt, terminal)
                    if key in table:
                        table[key].append(prod)
                    else:
                        table[key] = [prod]
                
                # If ε in FIRST(prod), add entries for FOLLOW(nt)
                if 'ε' in first_prod:
                    for terminal in self.follow_sets[nt]:
                        key = (nt, terminal)
                        if key in table:
                            table[key].append(prod)
                        else:
                            table[key] = [prod]
        
        return table
    
    def _detect_conflicts(self) -> List[str]:
        conflicts = []
        
        for key, prods in self.parsing_table.items():
            if len(prods) > 1:
                nt, term = key
                prod_strs = [' '.join(p) if p else 'ε' for p in prods]
                conflicts.append(
                    f"Conflict at ({nt}, {term}): multiple productions {prod_strs}"
                )
        
        return conflicts
    
    def is_ll1(self) -> bool:
        return len(self.conflicts) == 0
    
    def parse(self, tokens: List[str]) -> Tuple[bool, List[Dict], Optional[str]]:
      
        if not tokens or tokens[-1] != '$':
            tokens = tokens + ['$']
        
        stack = ['$', self.grammar.start_symbol]
        trace = []
        input_ptr = 0
        
        while stack:
            top = stack[-1]
            current = tokens[input_ptr] if input_ptr < len(tokens) else '$'
            
            # Record state
            step = {
                'stack': list(stack),
                'input': tokens[input_ptr:],
                'action': '',
                'production': None
            }
            
            if top == current:
                # Match
                step['action'] = f"Match {top}"
                stack.pop()
                input_ptr += 1
            elif self.grammar.is_terminal(top):
                # Mismatch
                step['action'] = f"Error: expected {top}, got {current}"
                trace.append(step)
                return False, trace, self._error_message(top, current, input_ptr)
            elif self.grammar.is_nonterminal(top):
                # Table lookup
                key = (top, current)
                if key not in self.parsing_table:
                    step['action'] = f"Error: no entry for ({top}, {current})"
                    trace.append(step)
                    expected = self._get_expected_tokens(top)
                    return False, trace, self._error_message_with_expected(
                        current, input_ptr, expected
                    )
                
                prods = self.parsing_table[key]
                prod = prods[0]  
                
                prod_str = ' '.join(prod) if prod else 'ε'
                step['action'] = f"Apply {top} -> {prod_str}"
                step['production'] = (top, prod)
                
                stack.pop()
                if prod:  
                    stack.extend(reversed(prod))
            else:
                step['action'] = f"Error: unknown symbol {top}"
                trace.append(step)
                return False, trace, f"Unknown symbol: {top}"
            
            trace.append(step)
        
        return True, trace, None
    
    def _get_expected_tokens(self, nonterminal: str) -> Set[str]:
        expected = set()
        for (nt, term), _ in self.parsing_table.items():
            if nt == nonterminal:
                expected.add(term)
        return expected
    
    def _error_message(self, expected: str, got: str, position: int) -> str:
        return f"Parse error at position {position}: expected {expected}, got {got}"
    
    def _error_message_with_expected(self, got: str, position: int, 
                                     expected: Set[str]) -> str:
        expected_str = ', '.join(sorted(expected))
        return (f"Parse error at position {position}: unexpected token '{got}'. "
                f"Expected one of: {{{expected_str}}}")
