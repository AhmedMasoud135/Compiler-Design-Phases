# 🖥️ Compiler Design Suite

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green?style=for-the-badge)](https://docs.python.org/3/library/tkinter.html)
[![Status](https://img.shields.io/badge/Status-Completed-success?style=for-the-badge)]()

A comprehensive, interactive educational suite for compiler design, implemented in Python. This project visualizes and executes the three core phases of compilation: **Lexical Analysis**, **Syntax Analysis**, and **Semantic Analysis**.

## 📑 Table of Contents
- [Overview](#-overview)
- [Project Structure](#-project-structure)
- [Modules Detail](#-modules-detail)
  - [Phase 1: Lexical Analysis](#phase-1-lexical-analysis)
  - [Phase 2: Syntax Analysis (Parsing)](#phase-2-syntax-analysis-parsing)
  - [Phase 3: Semantic Analysis](#phase-3-semantic-analysis)
- [Installation & Usage](#-installation--usage)
- [License](#-license)

---

## 📖 Overview

This suite is designed to help students and developers understand the internal workings of a compiler. It provides graphical interfaces (GUI) for each phase, allowing users to:
1.  **Tokenize** source code and view generated tokens.
2.  **Parse** grammars using LL(1), LR(0), and SLR(1) algorithms, visualizing Parse Trees and DFA automata.
3.  **Analyze** semantics, checking for type mismatches and scope errors while viewing the AST and Symbol Table.

---

## 📂 Project Structure

The codebase is organized into three distinct directories, each representing a compiler phase:

```text
Compiler-Design-Suite/
│
├── README.md                  # Project documentation
├── requirements.txt           # Python dependencies
│
├── 📂 Lexical/                # Phase 1: Tokenization
│   ├── main.py                # CLI Entry point
│   ├── GUI.py                 # Graphical Interface
│   ├── parse.csv              # Token output
│   └── test.c                 # Sample C source code
│
├── 📂 Parsing/                # Phase 2: Syntax Analysis
│   ├── main.py                # Entry point
│   ├── ui.py                  # Main Parser GUI
│   ├── ll1_parser.py          # LL(1) Logic & Table Generation
│   ├── lr_parser.py           # LR(0) & SLR(1) Logic
│   ├── visualizer.py          # DFA & Tree Visualization (Tkinter Canvas)
│   ├── grammar_transforms.py  # Left Recursion Removal & Left Factoring
│   ├── first_follow.py        # FIRST & FOLLOW Set Computation
│   └── backtracking_parser.py # Recursive Descent Parser
│
└── 📂 Semantic/               # Phase 3: Semantic Analysis
    ├── main.py                # Entry point
    ├── semantic_analyzer.py   # Type Checking & Scope Logic
    ├── visualization.py       # AST & Symbol Table GUI
    ├── test_analyzer.py       # Unit Tests
    └── examples/              # Sample code files
```

---

## 🔍 Modules Detail

### Phase 1: Lexical Analysis
The **Lexer** scans source code (C-like syntax) and converts it into a stream of tokens.
*   **Key Features**:
    *   Regex-based pattern matching for keywords, identifiers, literals, and operators.
    *   Handling of single-line (`//`) and multi-line (`/* */`) comments.
    *   Exporting tokens to CSV format for the parser.

### Phase 2: Syntax Analysis (Parsing)
The core **Parser** module supports multiple algorithms and grammar transformations.
*   **Key Features**:
    *   **LL(1) Parser**: 
        *   Computes **FIRST** and **FOLLOW** sets.
        *   Generates Predictive Parsing Tables.
        *   **Auto-Transformation**: Automatically eliminates Left Recursion and performs Left Factoring.
    *   **LR Parsers (LR(0) / SLR(1))**:
        *   Generates Canonical Collection of LR Items.
        *   Constructs **ACTION** and **GOTO** tables.
        *   **DFA Visualization**: Renders the state machine using an interactive canvas.
    *   **Visualizer**: Draws derivation trees and parse trees dynamically.

### Phase 3: Semantic Analysis
The **Semantic Analyzer** validates the logical consistency of the parsed code.
*   **Key Features**:
    *   **Abstract Syntax Tree (AST)**: Builds and visualizes the hierarchical structure of the code.
    *   **Symbol Table**: Tracks variable declarations, types, scopes, and initialization status.
    *   **Error Detection**:
        *   Type Mismatches (e.g., `int x = "string";`).
        *   Undeclared Variables.
        *   Scope Violations.
        *   Uninitialized Variable Warnings.

---

## 🚀 Installation & Usage

### Prerequisites
*   **Python 3.7** or higher.
*   **Tkinter** (Usually included with Python).
*   **Graphviz** (Optional, if used for advanced image generation).

### Setup
1.  **Clone the repository**
    ```bash
    git clone https://github.com/yourusername/compiler-design-suite.git
    cd compiler-design-suite
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

### Running the Applications

#### 1️⃣ Run Lexical Analyzer
```bash
cd Lexical
python GUI.py
```

#### 2️⃣ Run Parsing Tool
```bash
cd Parsing
python main.py
```
*Select your parsing method (LL1/LR0/SLR1) from the dropdown menu.*

#### 3️⃣ Run Semantic Analyzer
```bash
cd Semantic
python visualization.py
```
*Load an example file from `examples/` and click "Analyze".*

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
*Developed as a comprehensive Compiler Design Course Project.*
