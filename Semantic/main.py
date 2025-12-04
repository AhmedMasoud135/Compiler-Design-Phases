import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from visualization import main

if __name__ == '__main__':
    print("=" * 60)
    print("  Semantic Analyzer - Compiler Design Project")
    print("=" * 60)
    print("\nLaunching GUI application...")
    print("\nFeatures:")
    print("  ✓ Type Checking")
    print("  ✓ Scope Resolution")
    print("  ✓ Semantic Error Detection")
    print("  ✓ Abstract Syntax Tree (AST) Visualization")
    print("  ✓ Symbol Table Management")
    print("  ✓ Interactive Code Editor")
    print("\n" + "=" * 60 + "\n")
    
    main()
