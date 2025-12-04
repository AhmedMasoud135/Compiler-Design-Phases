"""
Backtracking recursive descent parser.
"""

from typing import List, Tuple, Optional, Dict
from grammar_parser import Grammar


class BacktrackingParser:
    """Naive backtracking recursive descent parser."""
    
    def __init__(self, grammar: Grammar):
        """
        Initialize backtracking parser.
        
        Args:
            grammar: Grammar
        """
        self.grammar = grammar
        self.trace = []
        self.max_depth = 100
    
    def parse(self, tokens: List[str]) -> Tuple[bool, List[Dict], Optional[str]]:
        """
        Parse token sequence with backtracking.
        
        Args:
            tokens: List of tokens
            
        Returns:
            Tuple of (success, trace, error_message)
        """
        self.trace = []
        self.tokens = tokens
        self.pos = 0
        
        try:
            result = self._parse_nonterminal(self.grammar.start_symbol, 0)
            
            if result and self.pos == len(tokens):
                return True, self.trace, None
            else:
                return False, self.trace, f"Parse failed: only matched {self.pos}/{len(tokens)} tokens"
        except RecursionError:
            return False, self.trace, "Parse failed: maximum recursion depth exceeded"
    
    def _parse_nonterminal(self, nonterminal: str, depth: int) -> bool:
        """
        Try to parse a nonterminal.
        
        Args:
            nonterminal: Nonterminal to parse
            depth: Recursion depth
            
        Returns:
            True if successful
        """
        if depth > self.max_depth:
            raise RecursionError("Maximum depth exceeded")
        
        self.trace.append({
            'action': f"{'  ' * depth}Try {nonterminal}",
            'position': self.pos,
            'remaining': self.tokens[self.pos:] if self.pos < len(self.tokens) else []
        })
        
        # Try each production
        for prod_idx, prod in enumerate(self.grammar.productions[nonterminal]):
            saved_pos = self.pos
            
            prod_str = ' '.join(prod) if prod else 'ε'
            self.trace.append({
                'action': f"{'  ' * depth}Try production {nonterminal} -> {prod_str}",
                'position': self.pos,
                'remaining': self.tokens[self.pos:] if self.pos < len(self.tokens) else []
            })
            
            success = self._parse_production(prod, depth + 1)
            
            if success:
                self.trace.append({
                    'action': f"{'  ' * depth}Success {nonterminal} -> {prod_str}",
                    'position': self.pos,
                    'remaining': self.tokens[self.pos:] if self.pos < len(self.tokens) else []
                })
                return True
            
            # Backtrack
            self.pos = saved_pos
            self.trace.append({
                'action': f"{'  ' * depth}Backtrack from {nonterminal} -> {prod_str}",
                'position': self.pos,
                'remaining': self.tokens[self.pos:] if self.pos < len(self.tokens) else []
            })
        
        self.trace.append({
            'action': f"{'  ' * depth}Failed {nonterminal}",
            'position': self.pos,
            'remaining': self.tokens[self.pos:] if self.pos < len(self.tokens) else []
        })
        return False
    
    def _parse_production(self, production: List[str], depth: int) -> bool:
        """
        Try to parse a production body.
        
        Args:
            production: Production body
            depth: Recursion depth
            
        Returns:
            True if successful
        """
        if not production:  # Epsilon production
            return True
        
        for symbol in production:
            if self.grammar.is_terminal(symbol):
                if self.pos >= len(self.tokens) or self.tokens[self.pos] != symbol:
                    return False
                self.pos += 1
            elif self.grammar.is_nonterminal(symbol):
                if not self._parse_nonterminal(symbol, depth):
                    return False
        
        return True