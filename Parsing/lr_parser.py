from typing import Dict, List, Set, Tuple, Optional
from grammar_parser import Grammar
from first_follow import compute_follow_sets, compute_first_sets
from dataclasses import dataclass
import copy


@dataclass(frozen=True)
class LRItem:
    lhs: str    # Production head
    rhs: tuple  # Production body
    dot: int    # Position of dot
    
    def __str__(self):
        rhs_list = list(self.rhs) if self.rhs else []
        rhs_with_dot = rhs_list[:self.dot] + ['·'] + rhs_list[self.dot:]
        rhs_str = ' '.join(rhs_with_dot) if rhs_with_dot else '·'
        return f"{self.lhs} -> {rhs_str}"
    
    def is_complete(self) -> bool:
        return self.dot >= len(self.rhs)
    
    def next_symbol(self) -> Optional[str]:
        if self.is_complete():
            return None
        return self.rhs[self.dot]


class LRParser:
    
    def __init__(self, grammar: Grammar, parser_type: str = 'LR(0)'):
       
        self.grammar = self._augment_grammar(grammar)
        self.parser_type = parser_type
        self.states = []
        self.goto_table = {}
        self.action_table = {}
        self.conflicts = []
        
        # Compute FOLLOW for SLR(1)
        if parser_type == 'SLR(1)':
            first_sets = compute_first_sets(self.grammar)
            self.follow_sets = compute_follow_sets(self.grammar, first_sets)
        
        self._build_automaton()
        self._build_tables()
    
    def _augment_grammar(self, grammar: Grammar) -> Grammar:
      
        new_start = grammar.start_symbol + "'"
        while new_start in grammar.productions:
            new_start += "'"
        
        productions = copy.deepcopy(grammar.productions)
        productions[new_start] = [[grammar.start_symbol]]
        
        return Grammar(productions, new_start)
    
    def _closure(self, items: Set[LRItem]) -> Set[LRItem]:
       
        closure = set(items)
        changed = True
        
        while changed:
            changed = False
            for item in list(closure):
                next_sym = item.next_symbol()
                if next_sym and self.grammar.is_nonterminal(next_sym):
                    # Add items for productions of next_sym
                    for prod in self.grammar.productions[next_sym]:
                        new_item = LRItem(next_sym, tuple(prod), 0)
                        if new_item not in closure:
                            closure.add(new_item)
                            changed = True
        
        return closure
    
    def _goto(self, items: Set[LRItem], symbol: str) -> Set[LRItem]:
    
        moved = set()
        
        for item in items:
            if item.next_symbol() == symbol:
                # Move dot over symbol
                new_item = LRItem(item.lhs, item.rhs, item.dot + 1)
                moved.add(new_item)
        
        return self._closure(moved)
    
    def _build_automaton(self):
        # Initial state
        start_prod = self.grammar.productions[self.grammar.start_symbol][0]
        initial_item = LRItem(self.grammar.start_symbol, tuple(start_prod), 0)
        initial_state = self._closure({initial_item})
        
        self.states = [initial_state]
        unmarked = [0]
        
        while unmarked:
            state_idx = unmarked.pop(0)
            state = self.states[state_idx]
            
            # Find all symbols after dots
            symbols = set()
            for item in state:
                sym = item.next_symbol()
                if sym:
                    symbols.add(sym)
            
            # Compute goto for each symbol
            for symbol in symbols:
                new_state = self._goto(state, symbol)
                
                if not new_state:
                    continue
                
                # Check if state already exists
                try:
                    new_idx = self.states.index(new_state)
                except ValueError:
                    new_idx = len(self.states)
                    self.states.append(new_state)
                    unmarked.append(new_idx)
                
                self.goto_table[(state_idx, symbol)] = new_idx
    
    def _build_tables(self):
        for state_idx, state in enumerate(self.states):
            for item in state:
                if not item.is_complete():
                    # Shift items
                    next_sym = item.next_symbol()
                    if self.grammar.is_terminal(next_sym):
                        key = (state_idx, next_sym)
                        next_state = self.goto_table.get((state_idx, next_sym))
                        if next_state is not None:
                            self._add_action(key, ('shift', next_state))
                else:
                    # Reduce items
                    if item.lhs == self.grammar.start_symbol:
                        # Accept
                        self._add_action((state_idx, '$'), ('accept', None))
                    else:
                        # Reduce
                        prod_num = self._get_production_number(item.lhs, item.rhs)
                        
                        if self.parser_type == 'LR(0)':
                            # Reduce on all terminals
                            for terminal in self.grammar.terminals:
                                self._add_action((state_idx, terminal), 
                                               ('reduce', prod_num, item.lhs, item.rhs))
                        else:  # SLR(1)
                            # Reduce on FOLLOW(lhs)
                            for terminal in self.follow_sets[item.lhs]:
                                self._add_action((state_idx, terminal),
                                               ('reduce', prod_num, item.lhs, item.rhs))
    
    def _add_action(self, key: Tuple[int, str], action: tuple):
        if key in self.action_table:
            existing = self.action_table[key]
            if existing != action:
                self.conflicts.append({
                    'state': key[0],
                    'symbol': key[1],
                    'existing': existing,
                    'new': action
                })
        else:
            self.action_table[key] = action
    
    def _get_production_number(self, lhs: str, rhs: tuple) -> int:
        count = 0
        for nt, prods in self.grammar.productions.items():
            for prod in prods:
                if nt == lhs and tuple(prod) == rhs:
                    return count
                count += 1
        return -1
    
    def has_conflicts(self) -> bool:
        return len(self.conflicts) > 0
    
    def get_reduction_states(self) -> Set[int]:
        reduction_states = set()
        for state_idx, state in enumerate(self.states):
            for item in state:
                if item.is_complete() and item.lhs != self.grammar.start_symbol:
                    reduction_states.add(state_idx)
                    break
        return reduction_states
    
    def parse(self, tokens: List[str]) -> Tuple[bool, List[Dict], Optional[str]]:
       
        if not tokens or tokens[-1] != '$':
            tokens = tokens + ['$']
        
        stack = [0]  # State stack
        symbol_stack = []  # Symbol stack
        trace = []
        input_ptr = 0
        
        while True:
            state = stack[-1]
            current = tokens[input_ptr] if input_ptr < len(tokens) else '$'
            
            step = {
                'stack': list(stack),
                'symbols': list(symbol_stack),
                'input': tokens[input_ptr:],
                'action': ''
            }
            
            key = (state, current)
            if key not in self.action_table:
                step['action'] = f"Error: no action for state {state}, symbol {current}"
                trace.append(step)
                return False, trace, f"Parse error at position {input_ptr}: unexpected '{current}'"
            
            action = self.action_table[key]
            
            if action[0] == 'shift':
                next_state = action[1]
                step['action'] = f"Shift {next_state}"
                stack.append(next_state)
                symbol_stack.append(current)
                input_ptr += 1
            elif action[0] == 'reduce':
                prod_num, lhs, rhs = action[1], action[2], action[3]
                rhs_str = ' '.join(rhs) if rhs else 'ε'
                step['action'] = f"Reduce by {lhs} -> {rhs_str}"
                
                # Pop states
                pop_count = len(rhs) if rhs else 0
                for _ in range(pop_count):
                    stack.pop()
                    if symbol_stack:
                        symbol_stack.pop()
                
                # Push lhs
                symbol_stack.append(lhs)
                
                # Goto
                goto_key = (stack[-1], lhs)
                if goto_key not in self.goto_table:
                    step['action'] += " (Error: no goto)"
                    trace.append(step)
                    return False, trace, f"Parse error: no goto for ({stack[-1]}, {lhs})"
                
                stack.append(self.goto_table[goto_key])
            elif action[0] == 'accept':
                step['action'] = "Accept"
                trace.append(step)
                return True, trace, None
            
            trace.append(step)
            
            # Safety check
            if len(trace) > 1000:
                return False, trace, "Parse exceeded maximum steps"
