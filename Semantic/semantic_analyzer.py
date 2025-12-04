import re
from typing import Dict, List, Any, Optional, Tuple

# Configuration Constants
DATA_TYPES = {
    "INT": "int",
    "FLOAT": "float",
    "STRING": "string",
    "BOOL": "bool",
    "VOID": "void",
    "UNKNOWN": "unknown"
}


NODE_TYPES = {
    "PROGRAM": "program",
    "DECLARATION": "declaration",
    "ASSIGNMENT": "assignment",
    "EXPRESSION": "expression",
    "BINARY_OP": "binary_op",
    "FUNCTION_DECL": "function_decl",
    "FUNCTION_CALL": "function_call",
    "IDENTIFIER": "identifier",
    "LITERAL": "literal",
    "BLOCK": "block"
}


def create_symbol(name, data_type, scope_level, is_initialized=False, 
                  is_function=False, parameters=None, line_number=0):
    return {
        'name': name,
        'data_type': data_type,
        'scope_level': scope_level,
        'is_initialized': is_initialized,
        'is_function': is_function,
        'parameters': parameters if parameters else [],
        'line_number': line_number
    }

def create_ast_node(node_type, value=None, data_type=DATA_TYPES["UNKNOWN"], 
                    children=None, line_number=0, attributes=None):
    return {
        'node_type': node_type,
        'value': value,
        'data_type': data_type,
        'children': children if children else [],
        'line_number': line_number,
        'attributes': attributes if attributes else {}
    }

def create_semantic_error(error_type, message, line_number, severity="error"):
    return {
        'error_type': error_type,
        'message': message,
        'line_number': line_number,
        'severity': severity
    }

def create_symbol_table():
    return {
        'scopes': [{}],  
        'current_scope_level': 0
    }


def enter_scope(symbol_table):
    symbol_table['scopes'].append({})
    symbol_table['current_scope_level'] += 1

def exit_scope(symbol_table):
    if symbol_table['current_scope_level'] > 0:
        symbol_table['scopes'].pop()
        symbol_table['current_scope_level'] -= 1

def add_symbol(symbol_table, symbol):
    current_level = symbol_table['current_scope_level']
    symbol_name = symbol['name']

    if symbol_name in symbol_table['scopes'][current_level]:
        return False

    symbol['scope_level'] = current_level
    symbol_table['scopes'][current_level][symbol_name] = symbol
    return True

def lookup_symbol(symbol_table, name):
    for scope_level in range(symbol_table['current_scope_level'], -1, -1):
        if name in symbol_table['scopes'][scope_level]:
            return symbol_table['scopes'][scope_level][name]
    return None

def get_all_symbols(symbol_table):
    symbols = []
    for scope in symbol_table['scopes']:
        symbols.extend(scope.values())
    return symbols


def parse_source_code(source_code):
    root = create_ast_node(NODE_TYPES["PROGRAM"], value="main")
    lines = source_code.strip().split('\n')

    line_number = 0
    for line in lines:
        line_number += 1
        line = line.strip()
        if not line or line.startswith('//'):
            continue

        node = parse_line(line, line_number)
        if node:
            root['children'].append(node)

    return root


def parse_line(line, line_number):
    decl_pattern = r'^(int|float|string|bool)\s+(\w+)\s*;'
    match = re.match(decl_pattern, line)
    if match:
        data_type_str, var_name = match.groups()
        node = create_ast_node(
            NODE_TYPES["DECLARATION"],
            value=var_name,
            data_type=data_type_str,
            line_number=line_number
        )
        return node

    init_pattern = r'^(int|float|string|bool)\s+(\w+)\s*=\s*(.+);'
    match = re.match(init_pattern, line)
    if match:
        data_type_str, var_name, expr = match.groups()
        node = create_ast_node(
            NODE_TYPES["DECLARATION"],
            value=var_name,
            data_type=data_type_str,
            line_number=line_number
        )
        expr_node = parse_expression(expr.strip(), line_number)
        assign_node = create_ast_node(
            NODE_TYPES["ASSIGNMENT"],
            value=var_name,
            line_number=line_number,
            children=[expr_node]
        )
        node['children'].append(assign_node)
        node['attributes']['initialized'] = True
        return node

    assign_pattern = r'^(\w+)\s*=\s*(.+);'
    match = re.match(assign_pattern, line)
    if match:
        var_name, expr = match.groups()
        expr_node = parse_expression(expr.strip(), line_number)
        node = create_ast_node(
            NODE_TYPES["ASSIGNMENT"],
            value=var_name,
            line_number=line_number,
            children=[expr_node]
        )
        return node

    func_pattern = r'^(int|float|string|bool|void)\s+(\w+)\s*\(([^)]*)\)'
    match = re.match(func_pattern, line)
    if match:
        return_type_str, func_name, params = match.groups()
        node = create_ast_node(
            NODE_TYPES["FUNCTION_DECL"],
            value=func_name,
            data_type=return_type_str,
            line_number=line_number
        )
        param_types = []
        if params.strip():
            for param in params.split(','):
                param = param.strip()
                if param:
                    parts = param.split()
                    if len(parts) >= 2:
                        param_types.append(parts[0])
        node['attributes']['param_types'] = param_types
        return node

    call_pattern = r'^(\w+)\s*\(([^)]*)\)\s*;'
    match = re.match(call_pattern, line)
    if match:
        func_name, args = match.groups()
        node = create_ast_node(
            NODE_TYPES["FUNCTION_CALL"],
            value=func_name,
            line_number=line_number
        )
        if args.strip():
            for arg in args.split(','):
                arg_node = parse_expression(arg.strip(), line_number)
                node['children'].append(arg_node)
        return node

    return None

def parse_expression(expr, line_number):
    expr = expr.strip()

    if re.match(r'^\d+$', expr):
        return create_ast_node(
            NODE_TYPES["LITERAL"],
            value=int(expr),
            data_type=DATA_TYPES["INT"],
            line_number=line_number
        )

    if re.match(r'^\d+\.\d+$', expr):
        return create_ast_node(
            NODE_TYPES["LITERAL"],
            value=float(expr),
            data_type=DATA_TYPES["FLOAT"],
            line_number=line_number
        )

    if (expr.startswith('"') and expr.endswith('"')) or \
       (expr.startswith("'") and expr.endswith("'")):
        return create_ast_node(
            NODE_TYPES["LITERAL"],
            value=expr[1:-1],
            data_type=DATA_TYPES["STRING"],
            line_number=line_number
        )

    if expr in ['true', 'false']:
        return create_ast_node(
            NODE_TYPES["LITERAL"],
            value=expr == 'true',
            data_type=DATA_TYPES["BOOL"],
            line_number=line_number
        )

    for op in ['+', '-', '*', '/', '%', '==', '!=', '<', '>', '<=', '>=']:
        if op in expr:
            parts = expr.split(op, 1)
            if len(parts) == 2:
                left = parse_expression(parts[0].strip(), line_number)
                right = parse_expression(parts[1].strip(), line_number)
                return create_ast_node(
                    NODE_TYPES["BINARY_OP"],
                    value=op,
                    line_number=line_number,
                    children=[left, right]
                )

    if re.match(r'^\w+$', expr):
        return create_ast_node(
            NODE_TYPES["IDENTIFIER"],
            value=expr,
            line_number=line_number
        )

    return create_ast_node(
        NODE_TYPES["EXPRESSION"],
        value=expr,
        line_number=line_number
    )


def analyze_node(node, symbol_table, errors, warnings):

    if node['node_type'] == NODE_TYPES["DECLARATION"]:
        analyze_declaration(node, symbol_table, errors, warnings)

    elif node['node_type'] == NODE_TYPES["ASSIGNMENT"]:
        analyze_assignment(node, symbol_table, errors, warnings)

    elif node['node_type'] == NODE_TYPES["BINARY_OP"]:
        analyze_binary_op(node, symbol_table, errors, warnings)

    elif node['node_type'] == NODE_TYPES["FUNCTION_DECL"]:
        analyze_function_declaration(node, symbol_table, errors, warnings)

    elif node['node_type'] == NODE_TYPES["FUNCTION_CALL"]:
        analyze_function_call(node, symbol_table, errors, warnings)

    elif node['node_type'] == NODE_TYPES["IDENTIFIER"]:
        analyze_identifier(node, symbol_table, errors, warnings)

    elif node['node_type'] == NODE_TYPES["LITERAL"]:
        pass

    for child in node['children']:
        analyze_node(child, symbol_table, errors, warnings)

def analyze_declaration(node, symbol_table, errors, warnings):
    var_name = node['value']
    var_type = node['data_type']

    existing = lookup_symbol(symbol_table, var_name)
    if existing and existing['scope_level'] == symbol_table['current_scope_level']:
        errors.append(create_semantic_error(
            "Redeclaration",
            f"Variable '{var_name}' is already declared in this scope",
            node['line_number']
        ))
        return

    is_initialized = node['attributes'].get('initialized', False)
    symbol = create_symbol(
        name=var_name,
        data_type=var_type,
        scope_level=symbol_table['current_scope_level'],
        is_initialized=is_initialized,
        line_number=node['line_number']
    )
    add_symbol(symbol_table, symbol)

def analyze_assignment(node, symbol_table, errors, warnings):
    var_name = node['value']

    symbol = lookup_symbol(symbol_table, var_name)
    if not symbol:
        errors.append(create_semantic_error(
            "Undeclared Variable",
            f"Variable '{var_name}' is used before declaration",
            node['line_number']
        ))
        return

    symbol['is_initialized'] = True

    if node['children']:
        expr_node = node['children'][0]
        expr_type = infer_type(expr_node, symbol_table)

        if expr_type != DATA_TYPES["UNKNOWN"] and symbol['data_type'] != expr_type:
            errors.append(create_semantic_error(
                "Type Mismatch",
                f"Cannot assign {expr_type} to {symbol['data_type']} variable '{var_name}'",
                node['line_number']
            ))

def analyze_binary_op(node, symbol_table, errors, warnings):
    if len(node['children']) < 2:
        return

    left_type = infer_type(node['children'][0], symbol_table)
    right_type = infer_type(node['children'][1], symbol_table)

    if left_type != DATA_TYPES["UNKNOWN"] and right_type != DATA_TYPES["UNKNOWN"]:
        if left_type != right_type:
            warnings.append(create_semantic_error(
                "Type Compatibility",
                f"Operation '{node['value']}' between {left_type} and {right_type} may cause issues",
                node['line_number'],
                severity="warning"
            ))

    if node['value'] in ['==', '!=', '<', '>', '<=', '>=']:
        node['data_type'] = DATA_TYPES["BOOL"]
    elif left_type == DATA_TYPES["FLOAT"] or right_type == DATA_TYPES["FLOAT"]:
        node['data_type'] = DATA_TYPES["FLOAT"]
    else:
        node['data_type'] = left_type

def analyze_function_declaration(node, symbol_table, errors, warnings):
    func_name = node['value']
    return_type = node['data_type']
    param_types = node['attributes'].get('param_types', [])

    existing = lookup_symbol(symbol_table, func_name)
    if existing:
        errors.append(create_semantic_error(
            "Redeclaration",
            f"Function '{func_name}' is already declared",
            node['line_number']
        ))
        return

    symbol = create_symbol(
        name=func_name,
        data_type=return_type,
        scope_level=symbol_table['current_scope_level'],
        is_function=True,
        parameters=param_types,
        line_number=node['line_number']
    )
    add_symbol(symbol_table, symbol)

def analyze_function_call(node, symbol_table, errors, warnings):
    func_name = node['value']

    symbol = lookup_symbol(symbol_table, func_name)
    if not symbol:
        errors.append(create_semantic_error(
            "Undeclared Function",
            f"Function '{func_name}' is not declared",
            node['line_number']
        ))
        return

    if not symbol['is_function']:
        errors.append(create_semantic_error(
            "Not a Function",
            f"'{func_name}' is not a function",
            node['line_number']
        ))
        return

    arg_count = len(node['children'])
    param_count = len(symbol['parameters'])

    if arg_count != param_count:
        errors.append(create_semantic_error(
            "Argument Count Mismatch",
            f"Function '{func_name}' expects {param_count} arguments but got {arg_count}",
            node['line_number']
        ))
        return

    for i, (arg_node, expected_type) in enumerate(zip(node['children'], symbol['parameters'])):
        arg_type = infer_type(arg_node, symbol_table)
        if arg_type != DATA_TYPES["UNKNOWN"] and arg_type != expected_type:
            errors.append(create_semantic_error(
                "Type Mismatch",
                f"Argument {i+1} of function '{func_name}': expected {expected_type}, got {arg_type}",
                node['line_number']
            ))

def analyze_identifier(node, symbol_table, errors, warnings):
    var_name = node['value']

    if node['node_type'] == NODE_TYPES["LITERAL"]:
        return

    symbol = lookup_symbol(symbol_table, var_name)
    if not symbol:
        errors.append(create_semantic_error(
            "Undeclared Variable",
            f"Variable '{var_name}' is not declared",
            node['line_number']
        ))
        return

    if not symbol['is_initialized'] and not symbol['is_function']:
        warnings.append(create_semantic_error(
            "Uninitialized Variable",
            f"Variable '{var_name}' may be used before initialization",
            node['line_number'],
            severity="warning"
        ))

    node['data_type'] = symbol['data_type']

def infer_type(node, symbol_table):
    if node['data_type'] != DATA_TYPES["UNKNOWN"]:
        return node['data_type']

    if node['node_type'] == NODE_TYPES["IDENTIFIER"]:
        symbol = lookup_symbol(symbol_table, node['value'])
        if symbol:
            return symbol['data_type']

    elif node['node_type'] == NODE_TYPES["BINARY_OP"]:
        if node['value'] in ['==', '!=', '<', '>', '<=', '>=']:
            return DATA_TYPES["BOOL"]
        left_type = infer_type(node['children'][0], symbol_table) if node['children'] else DATA_TYPES["UNKNOWN"]
        right_type = infer_type(node['children'][1], symbol_table) if len(node['children']) > 1 else DATA_TYPES["UNKNOWN"]
        if left_type == DATA_TYPES["FLOAT"] or right_type == DATA_TYPES["FLOAT"]:
            return DATA_TYPES["FLOAT"]
        return left_type

    return DATA_TYPES["UNKNOWN"]


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = create_symbol_table()
        self.errors = []
        self.warnings = []
        self.ast = None

    def analyze(self, source_code):
        self.errors = []
        self.warnings = []
        self.symbol_table = create_symbol_table()

        self.ast = parse_source_code(source_code)

        if self.ast:
            analyze_node(self.ast, self.symbol_table, self.errors, self.warnings)

        return self.ast, self.errors, self.warnings

    def get_symbol_table_info(self):
        symbols = get_all_symbols(self.symbol_table)
        return [
            {
                'name': s['name'],
                'type': s['data_type'],
                'scope': s['scope_level'],
                'initialized': s['is_initialized'],
                'is_function': s['is_function'],
                'line': s['line_number']
            }
            for s in symbols
        ]

    def get_ast_structure(self):
        def node_to_dict(node):
            return {
                'type': node['node_type'],
                'value': str(node['value']) if node['value'] else '',
                'data_type': node['data_type'],
                'line': node['line_number'],
                'children': [node_to_dict(child) for child in node['children']]
            }

        if self.ast:
            return node_to_dict(self.ast)
        return {}


def format_error(error):
    severity_symbol = "ERROR" if error['severity'] == "error" else "WARNING"
    return f"[{severity_symbol}] Line {error['line_number']}: {error['error_type']} - {error['message']}"

def print_symbol_table(symbol_table):
    symbols = get_all_symbols(symbol_table)
    print("\n" + "="*80)
    print("SYMBOL TABLE")
    print("="*80)
    print(f"{'Name':<20} {'Type':<10} {'Scope':<8} {'Init':<8} {'Function':<10} {'Line':<6}")
    print("-"*80)
    for s in symbols:
        print(f"{s['name']:<20} {s['data_type']:<10} {s['scope_level']:<8} "
              f"{'Yes' if s['is_initialized'] else 'No':<8} "
              f"{'Yes' if s['is_function'] else 'No':<10} {s['line_number']:<6}")
    print("="*80)

def print_ast(node, indent=0):
    prefix = "  " * indent
    print(f"{prefix}{node['node_type']} ({node['data_type']}): {node['value']}")
    for child in node['children']:
        print_ast(child, indent + 1)


# EXAMPLE 

if __name__ == "__main__":
    test_code = """
    int x;
    int y = 10;
    float z = 3.14;
    x = y + 5;
    string name = "test";
    int add(int a, int b)
    add(x, y);
    int result = x + z;
    """

    analyzer = SemanticAnalyzer()
    ast, errors, warnings = analyzer.analyze(test_code)

    print("\nSemantic Analysis Results:")
    print("="*80)

    if errors:
        print("\nERRORS:")
        for error in errors:
            print(f"  {format_error(error)}")
    else:
        print("\nNo errors found!")

    if warnings:
        print("\nWARNINGS:")
        for warning in warnings:
            print(f"  {format_error(warning)}")

    print("\n" + "="*80)
    print("Symbol Table:")
    symbols = analyzer.get_symbol_table_info()
    for s in symbols:
        print(f"  {s['name']} ({s['type']}) - Line {s['line']}")

    print("\n" + "="*80)
    print("AST Structure:")
    if ast:
        print_ast(ast)