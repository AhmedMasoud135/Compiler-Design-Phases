"""
CSV token import/export handler.
"""

import csv
from typing import List, Dict, Tuple, Optional
from io import StringIO


class CSVHandler:    
    @staticmethod
    def import_tokens(csv_content: str) -> Tuple[List[str], List[Dict], Optional[str]]:
        """
        Import tokens from CSV content.
        
        Expected format:
        token,lexeme,position
        int,3,1
        +,+,2

        """
        try:
            reader = csv.DictReader(StringIO(csv_content))
            
            if 'token' not in reader.fieldnames:
                return [], [], "CSV must have 'token' column"
            
            tokens = []
            full_data = []
            
            for row in reader:
                if 'token' not in row or not row['token']:
                    continue
                
                tokens.append(row['token'])
                full_data.append(dict(row))
            
            if not tokens:
                return [], [], "No tokens found in CSV"
            
            return tokens, full_data, None
            
        except Exception as e:
            return [], [], f"Error parsing CSV: {str(e)}"
    
    @staticmethod
    def export_tokens(tokens: List[str], lexemes: List[str] = None) -> str:
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        if lexemes:
            writer.writerow(['token', 'lexeme', 'position'])
        else:
            writer.writerow(['token', 'position'])
        
        # Rows
        for i, token in enumerate(tokens):
            if lexemes and i < len(lexemes):
                writer.writerow([token, lexemes[i], i + 1])
            else:
                writer.writerow([token, i + 1])
        
        return output.getvalue()
    
    @staticmethod
    def export_parsing_table(table: Dict, nonterminals: List[str], 
                            terminals: List[str]) -> str:
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([''] + terminals)
        
        # Rows
        for nt in nonterminals:
            row = [nt]
            for term in terminals:
                key = (nt, term)
                if key in table:
                    prods = table[key]
                    if len(prods) == 1:
                        prod = prods[0]
                        prod_str = ' '.join(prod) if prod else 'ε'
                        row.append(f"{nt} -> {prod_str}")
                    else:
                        row.append("CONFLICT")
                else:
                    row.append('')
            writer.writerow(row)
        
        return output.getvalue()
    
    @staticmethod
    def export_trace(trace: List[Dict]) -> str:

        output = StringIO()
        writer = csv.writer(output)
        
        # Determine columns
        if trace:
            columns = list(trace[0].keys())
            writer.writerow(columns)
            
            for step in trace:
                row = []
                for col in columns:
                    value = step.get(col, '')
                    if isinstance(value, list):
                        value = ' '.join(str(v) for v in value)
                    row.append(str(value))
                writer.writerow(row)
        
        return output.getvalue()
    
    @staticmethod
    def validate_tokens_against_grammar(tokens: List[str], 
                                       grammar_terminals: set) -> List[str]:
    
        warnings = []
        
        for i, token in enumerate(tokens):
            if token not in grammar_terminals and token != '$':
                warnings.append(
                    f"Warning: Token '{token}' at position {i+1} not in grammar terminals"
                )
        
        return warnings
