"""
Test Suite for Semantic Analyzer
Run this to verify the semantic analyzer is working correctly
"""

from semantic_analyzer import SemanticAnalyzer, DataType


def test_basic_declarations():
    """Test basic variable declarations"""
    print("\n" + "="*60)
    print("Test 1: Basic Variable Declarations")
    print("="*60)
    
    code = """
int x;
float y = 3.14;
string name = "John";
bool flag = true;
"""
    
    analyzer = SemanticAnalyzer()
    ast, errors, warnings = analyzer.analyze(code)
    
    print(f"Code:\n{code}")
    print(f"\nErrors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")
    print(f"Symbols: {len(analyzer.get_symbol_table_info())}")
    
    for error in errors:
        print(f"  ❌ Line {error.line_number}: {error.message}")
    for warning in warnings:
        print(f"  ⚠️  Line {warning.line_number}: {warning.message}")
        
    assert len(errors) == 0, "Should have no errors"
    print("✓ Test passed!")


def test_undeclared_variable():
    """Test undeclared variable detection"""
    print("\n" + "="*60)
    print("Test 2: Undeclared Variable Detection")
    print("="*60)
    
    code = """
int x = 5;
y = 10;
"""
    
    analyzer = SemanticAnalyzer()
    ast, errors, warnings = analyzer.analyze(code)
    
    print(f"Code:\n{code}")
    print(f"\nErrors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")
    
    for error in errors:
        print(f"  ❌ Line {error.line_number}: {error.message}")
        
    assert len(errors) > 0, "Should detect undeclared variable"
    assert any("not declared" in e.message.lower() or "before declaration" in e.message.lower() for e in errors)
    print("✓ Test passed!")


def test_type_mismatch():
    """Test type mismatch detection"""
    print("\n" + "="*60)
    print("Test 3: Type Mismatch Detection")
    print("="*60)
    
    code = """
int x = 5;
x = "hello";
"""
    
    analyzer = SemanticAnalyzer()
    ast, errors, warnings = analyzer.analyze(code)
    
    print(f"Code:\n{code}")
    print(f"\nErrors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")
    
    for error in errors:
        print(f"  ❌ Line {error.line_number}: {error.message}")
        
    assert len(errors) > 0, "Should detect type mismatch"
    assert any("cannot assign" in e.message.lower() or "type" in e.message.lower() or "mismatch" in e.message.lower() for e in errors)
    print("✓ Test passed!")


def test_function_declaration_and_call():
    """Test function declaration and call"""
    print("\n" + "="*60)
    print("Test 4: Function Declaration and Call")
    print("="*60)
    
    code = """
int add(int a, int b);
int x = 5;
int y = 10;
add(x, y);
"""
    
    analyzer = SemanticAnalyzer()
    ast, errors, warnings = analyzer.analyze(code)
    
    print(f"Code:\n{code}")
    print(f"\nErrors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")
    
    for error in errors:
        print(f"  ❌ Line {error.line_number}: {error.message}")
        
    assert len(errors) == 0, "Should have no errors"
    print("✓ Test passed!")


def test_function_argument_mismatch():
    """Test function argument count mismatch"""
    print("\n" + "="*60)
    print("Test 5: Function Argument Mismatch")
    print("="*60)
    
    code = """
int add(int a, int b);
int x = 5;
add(x);
"""
    
    analyzer = SemanticAnalyzer()
    ast, errors, warnings = analyzer.analyze(code)
    
    print(f"Code:\n{code}")
    print(f"\nErrors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")
    
    for error in errors:
        print(f"  ❌ Line {error.line_number}: {error.message}")
        
    assert len(errors) > 0, "Should detect argument mismatch"
    assert any("argument" in e.message.lower() for e in errors)
    print("✓ Test passed!")


def test_uninitialized_variable():
    """Test uninitialized variable warning"""
    print("\n" + "="*60)
    print("Test 6: Uninitialized Variable Warning")
    print("="*60)
    
    code = """
int x;
int y = x + 5;
"""
    
    analyzer = SemanticAnalyzer()
    ast, errors, warnings = analyzer.analyze(code)
    
    print(f"Code:\n{code}")
    print(f"\nErrors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")
    
    for warning in warnings:
        print(f"  ⚠️  Line {warning.line_number}: {warning.message}")
        
    assert len(warnings) > 0, "Should warn about uninitialized variable"
    print("✓ Test passed!")


def test_redeclaration():
    """Test variable redeclaration detection"""
    print("\n" + "="*60)
    print("Test 7: Variable Redeclaration")
    print("="*60)
    
    code = """
int x = 5;
int x = 10;
"""
    
    analyzer = SemanticAnalyzer()
    ast, errors, warnings = analyzer.analyze(code)
    
    print(f"Code:\n{code}")
    print(f"\nErrors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")
    
    for error in errors:
        print(f"  ❌ Line {error.line_number}: {error.message}")
        
    assert len(errors) > 0, "Should detect redeclaration"
    assert any("already declared" in e.message.lower() for e in errors)
    print("✓ Test passed!")


def test_complex_expressions():
    """Test complex expressions"""
    print("\n" + "="*60)
    print("Test 8: Complex Expressions")
    print("="*60)
    
    code = """
int a = 5;
int b = 10;
int c = 15;
int result = a + b * c;
bool comparison = a < b;
"""
    
    analyzer = SemanticAnalyzer()
    ast, errors, warnings = analyzer.analyze(code)
    
    print(f"Code:\n{code}")
    print(f"\nErrors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")
    
    for error in errors:
        print(f"  ❌ Line {error.line_number}: {error.message}")
        
    assert len(errors) == 0, "Should handle complex expressions"
    print("✓ Test passed!")


def test_symbol_table():
    """Test symbol table functionality"""
    print("\n" + "="*60)
    print("Test 9: Symbol Table")
    print("="*60)
    
    code = """
int x = 5;
float y = 3.14;
string name = "Test";
int add(int a, int b);
"""
    
    analyzer = SemanticAnalyzer()
    ast, errors, warnings = analyzer.analyze(code)
    
    symbols = analyzer.get_symbol_table_info()
    
    print(f"Code:\n{code}")
    print(f"\nSymbol Table ({len(symbols)} entries):")
    print("-" * 60)
    print(f"{'Name':<15} {'Type':<10} {'Scope':<8} {'Init':<8} {'Kind':<12}")
    print("-" * 60)
    
    for symbol in symbols:
        kind = 'Function' if symbol['is_function'] else 'Variable'
        init = '✓' if symbol['initialized'] else '✗'
        print(f"{symbol['name']:<15} {symbol['type']:<10} {symbol['scope']:<8} {init:<8} {kind:<12}")
    
    assert len(symbols) == 4, "Should have 4 symbols"
    assert sum(1 for s in symbols if s['is_function']) == 1, "Should have 1 function"
    assert sum(1 for s in symbols if not s['is_function']) == 3, "Should have 3 variables"
    print("\n✓ Test passed!")


def test_ast_structure():
    """Test AST structure"""
    print("\n" + "="*60)
    print("Test 10: AST Structure")
    print("="*60)
    
    code = """
int x = 5;
int y = x + 10;
"""
    
    analyzer = SemanticAnalyzer()
    ast, errors, warnings = analyzer.analyze(code)
    
    ast_dict = analyzer.get_ast_structure()
    
    print(f"Code:\n{code}")
    print(f"\nAST Structure:")
    print(f"Root type: {ast_dict.get('type')}")
    print(f"Root value: {ast_dict.get('value')}")
    print(f"Children: {len(ast_dict.get('children', []))}")
    
    assert ast_dict.get('type') == 'program', "Root should be program"
    assert len(ast_dict.get('children', [])) > 0, "Should have children"
    print("✓ Test passed!")


def run_all_tests():
    """Run all tests"""
    print("\n")
    print("╔" + "="*60 + "╗")
    print("║" + " "*15 + "SEMANTIC ANALYZER TEST SUITE" + " "*17 + "║")
    print("╚" + "="*60 + "╝")
    
    tests = [
        test_basic_declarations,
        test_undeclared_variable,
        test_type_mismatch,
        test_function_declaration_and_call,
        test_function_argument_mismatch,
        test_uninitialized_variable,
        test_redeclaration,
        test_complex_expressions,
        test_symbol_table,
        test_ast_structure
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ Test error: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed out of {len(tests)} total")
    print("="*60)
    
    if failed == 0:
        print("\n🎉 All tests passed! The semantic analyzer is working correctly.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the errors above.")


if __name__ == '__main__':
    run_all_tests()
