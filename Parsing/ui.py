import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from typing import Optional, Dict, List
import json

from grammar_parser import parse_grammar, validate_grammar, DEFAULT_GRAMMAR, Grammar
from grammar_transforms import remove_left_recursion, left_factor, needs_transformation_for_ll1
from ll1_parser import LL1Parser
from lr_parser import LRParser
import visualizer
from csv_handler import CSVHandler

# Enhanced Royal Theme - Gold, White (Milky), Black
THEME = {
    'gold': '#D4AF37',
    'dark_gold': '#B8860B',
    'black': '#1C1C1C',
    'milky': '#FFF8E7',
    'white': '#FFFFFF',
    'bg': '#1C1C1C',
    'panel_bg': '#2A2A2A',
    'text': '#FFF8E7',
    'gold_text': '#D4AF37',
    'accent': '#D4AF37',
    'error': '#DC143C',
    'success': '#228B22',
    'normal_state': '#FFF8E7',
    'accept_state': '#90EE90',
    'start_state': '#FFD700',
    'state_text': '#1C1C1C',
    'label_bg': '#FFF8E7'
}

def create_root_window():
    """Create root window with theme."""
    root = tk.Tk()
    root.configure(bg=THEME['bg'])
    return root

def setup_styles():
    """Setup enhanced ttk styles."""
    style = ttk.Style()
    
    try:
        style.theme_use('clam')
    except:
        pass
    
    # Frame styles
    style.configure('TFrame', background=THEME['bg'])
    style.configure('Panel.TFrame', background=THEME['panel_bg'])
    
    # Label styles
    style.configure('TLabel', background=THEME['bg'], foreground=THEME['text'], font=('Arial', 10))
    style.configure('Header.TLabel', font=('Georgia', 24, 'bold'),
                   foreground=THEME['gold'], background=THEME['bg'])
    style.configure('Section.TLabel', font=('Arial', 13, 'bold'),
                   foreground=THEME['gold'], background=THEME['panel_bg'])
    style.configure('Info.TLabel', font=('Arial', 10),
                   foreground=THEME['text'], background=THEME['panel_bg'])
    
    # Button styles
    style.configure('Gold.TButton', font=('Arial', 11, 'bold'),
                   foreground=THEME['black'], background=THEME['gold'])
    style.map('Gold.TButton',
             background=[('active', THEME['dark_gold']),
                        ('pressed', THEME['dark_gold'])])
    
    # Notebook style
    style.configure('TNotebook', background=THEME['panel_bg'], borderwidth=0)
    style.configure('TNotebook.Tab', font=('Arial', 11, 'bold'),
                   padding=[20, 10])

def log_message(console_widget, message, level='INFO'):
    """Log message to console with color."""
    colors = {
        'INFO': THEME['gold'],
        'WARNING': '#FFA500',
        'ERROR': THEME['error'],
        'SUCCESS': THEME['success']
    }
    
    color = colors.get(level, THEME['text'])
    console_widget.insert(tk.END, f"[{level}] ", 'level')
    console_widget.tag_config('level', foreground=color, font=('Courier', 9, 'bold'))
    console_widget.insert(tk.END, f"{message}\n", 'message')
    console_widget.tag_config('message', foreground=THEME['text'])
    console_widget.see(tk.END)
    console_widget.update()

def build_ll1_parser(grammar, console_widget):
    """Build LL(1) parser."""
    log_message(console_widget, "Building LL(1) parser...")
    
    transformed_grammar = grammar
    if needs_transformation_for_ll1(grammar):
        log_message(console_widget, "Grammar needs transformation for LL(1)", 'WARNING')
        log_message(console_widget, "Removing left recursion...")
        transformed_grammar = remove_left_recursion(grammar)
        log_message(console_widget, "Performing left factoring...")
        transformed_grammar = left_factor(transformed_grammar)
        log_message(console_widget, "Grammar transformed successfully", 'SUCCESS')
    else:
        log_message(console_widget, "Grammar is suitable for LL(1)", 'SUCCESS')
    
    parser = LL1Parser(transformed_grammar)
    
    if parser.is_ll1():
        log_message(console_widget, "✓ Grammar is LL(1)", 'SUCCESS')
    else:
        log_message(console_widget, "✗ Grammar is NOT LL(1) - conflicts detected", 'ERROR')
        for conflict in parser.conflicts:
            log_message(console_widget, f"  {conflict}", 'ERROR')
    
    return parser, transformed_grammar

def build_lr_parser(grammar, technique, console_widget):
    """Build LR parser."""
    log_message(console_widget, f"Building {technique} parser...")
    
    parser = LRParser(grammar, technique)
    transformed_grammar = parser.grammar
    
    log_message(console_widget, f"Built {technique} automaton with {len(parser.states)} states", 'SUCCESS')
    
    if parser.has_conflicts():
        log_message(console_widget, f"✗ Grammar has conflicts", 'ERROR')
        for conflict in parser.conflicts[:5]:
            log_message(console_widget,
                       f"  State {conflict['state']}, symbol {conflict['symbol']}", 'ERROR')
        if len(parser.conflicts) > 5:
            log_message(console_widget, f"  ... and {len(parser.conflicts)-5} more conflicts", 'ERROR')
    else:
        log_message(console_widget, f"✓ Grammar is {technique}", 'SUCCESS')
    
    return parser, transformed_grammar

def format_ll1_table(parser, grammar):
    """Format LL(1) parsing table."""
    terminals = sorted(grammar.terminals)
    nonterminals = sorted(grammar.nonterminals)
    col_width = 18
    
    lines = []
    header = "NT".ljust(10) + " │ " + " │ ".join(t.center(col_width) for t in terminals)
    lines.append(header)
    lines.append("═" * len(header))
    
    for nt in nonterminals:
        row = nt.ljust(10) + " │ "
        cells = []
        
        for term in terminals:
            key = (nt, term)
            if key in parser.parsing_table:
                prods = parser.parsing_table[key]
                if len(prods) == 1:
                    prod = prods[0]
                    prod_str = ' '.join(prod) if prod else 'ε'
                    cell = f"{nt}→{prod_str}"
                else:
                    cell = "⚠CONFLICT"
            else:
                cell = "—"
            
            cells.append(cell.center(col_width))
        
        row += " │ ".join(cells)
        lines.append(row)
        lines.append("─" * len(header))
    
    return '\n'.join(lines)

def format_lr_combined_table(parser, grammar):
    """Format LR ACTION and GOTO table combined like the image."""
    terminals = sorted([t for t in grammar.terminals if t != '$']) + ['$']
    nonterminals = sorted(grammar.nonterminals)
    
    lines = []
    
    # Header
    header_parts = ["State".ljust(7)]
    header_parts.append("│")
    
    # ACTION columns
    action_headers = []
    for t in terminals:
        action_headers.append(t.center(12))
    header_parts.append(" ".join(action_headers))
    
    header_parts.append("║")
    
    # GOTO columns
    goto_headers = []
    for nt in nonterminals:
        goto_headers.append(nt.center(8))
    header_parts.append(" ".join(goto_headers))
    
    header = " ".join(header_parts)
    lines.append(header)
    lines.append("═" * len(header))
    
    # Rows for each state
    for state_idx in range(len(parser.states)):
        row_parts = [str(state_idx).ljust(7)]
        row_parts.append("│")
        
        # ACTION columns
        action_cells = []
        for term in terminals:
            key = (state_idx, term)
            if key in parser.action_table:
                action = parser.action_table[key]
                if action[0] == 'shift':
                    cell = f"s{action[1]}"
                elif action[0] == 'reduce':
                    cell = f"r{action[1]}"
                elif action[0] == 'accept':
                    cell = "acc"
                else:
                    cell = "—"
            else:
                cell = "—"
            action_cells.append(cell.center(12))
        row_parts.append(" ".join(action_cells))
        
        row_parts.append("║")
        
        # GOTO columns
        goto_cells = []
        for nt in nonterminals:
            key = (state_idx, nt)
            if key in parser.goto_table:
                cell = str(parser.goto_table[key])
            else:
                cell = "—"
            goto_cells.append(cell.center(8))
        row_parts.append(" ".join(goto_cells))
        
        row = " ".join(row_parts)
        lines.append(row)
    
    return '\n'.join(lines)

def display_ll1_results(parser, grammar, transformed_grammar, tables_text):
    """Display LL(1) results with enhanced formatting."""
    tables_text.delete('1.0', tk.END)
    
    # Configure tags
    tables_text.tag_config('header', foreground=THEME['gold'], font=('Courier', 11, 'bold'))
    tables_text.tag_config('subheader', foreground=THEME['gold'], font=('Courier', 10, 'bold'))
    tables_text.tag_config('normal', foreground=THEME['text'], font=('Courier', 9))
    tables_text.tag_config('production', foreground='#90EE90', font=('Courier', 9))
    
    # Grammar
    if transformed_grammar != grammar:
        tables_text.insert(tk.END, "╔═══ ORIGINAL GRAMMAR ═══╗\n", 'header')
        tables_text.insert(tk.END, str(grammar) + "\n\n", 'production')
        tables_text.insert(tk.END, "╔═══ TRANSFORMED GRAMMAR ═══╗\n", 'header')
        tables_text.insert(tk.END, str(transformed_grammar) + "\n\n", 'production')
    else:
        tables_text.insert(tk.END, "╔═══ GRAMMAR ═══╗\n", 'header')
        tables_text.insert(tk.END, str(grammar) + "\n\n", 'production')
    
    # FIRST sets
    tables_text.insert(tk.END, "╔═══ FIRST SETS ═══╗\n", 'header')
    for symbol in sorted(parser.first_sets.keys()):
        first_set = parser.first_sets[symbol]
        tables_text.insert(tk.END, f"FIRST({symbol}) = ", 'subheader')
        tables_text.insert(tk.END, f"{{{', '.join(sorted(first_set))}}}\n", 'normal')
    tables_text.insert(tk.END, "\n", 'normal')
    
    # FOLLOW sets
    tables_text.insert(tk.END, "╔═══ FOLLOW SETS ═══╗\n", 'header')
    for nt in sorted(parser.follow_sets.keys()):
        follow_set = parser.follow_sets[nt]
        tables_text.insert(tk.END, f"FOLLOW({nt}) = ", 'subheader')
        tables_text.insert(tk.END, f"{{{', '.join(sorted(follow_set))}}}\n", 'normal')
    tables_text.insert(tk.END, "\n", 'normal')
    
    # Parsing table
    tables_text.insert(tk.END, "╔═══ LL(1) PARSING TABLE ═══╗\n", 'header')
    tables_text.insert(tk.END, format_ll1_table(parser, transformed_grammar) + "\n", 'normal')

def display_lr_results(parser, transformed_grammar, tables_text, dfa_canvas):
    """Display LR results with enhanced formatting and ALL states."""
    tables_text.delete('1.0', tk.END)
    
    tables_text.tag_config('header', foreground=THEME['gold'], font=('Courier', 11, 'bold'))
    tables_text.tag_config('subheader', foreground=THEME['gold'], font=('Courier', 10, 'bold'))
    tables_text.tag_config('normal', foreground=THEME['text'], font=('Courier', 9))
    tables_text.tag_config('item', foreground='#90EE90', font=('Courier', 9))
    
    # Grammar
    tables_text.insert(tk.END, "╔═══ AUGMENTED GRAMMAR ═══╗\n", 'header')
    tables_text.insert(tk.END, str(transformed_grammar) + "\n\n", 'item')
    
    # ALL Item sets
    tables_text.insert(tk.END, f"╔═══ LR ITEM SETS (All {len(parser.states)} States) ═══╗\n", 'header')
    for i, state in enumerate(parser.states):
        tables_text.insert(tk.END, f"\n▸ State {i}:\n", 'subheader')
        for item in sorted(state, key=str):
            tables_text.insert(tk.END, f"  {item}\n", 'item')
    
    # Combined ACTION and GOTO table
    tables_text.insert(tk.END, "\n╔═══ COMBINED ACTION & GOTO TABLE ═══╗\n", 'header')
    tables_text.insert(tk.END, format_lr_combined_table(parser, transformed_grammar) + "\n", 'normal')
    
    # Draw DFA
    reduction_states = parser.get_reduction_states()
    visualizer.draw_dfa_sequential(dfa_canvas, parser.states, parser.goto_table,
                                   reduction_states, THEME)

def parse_tokens_handler(parser, transformed_grammar, tokens_str, console_widget,
                         trace_text, result_canvas):
    """Handle token parsing with result indicator."""
    if not parser:
        messagebox.showwarning("Warning", "Build parser first!")
        return None
    
    try:
        tokens = tokens_str.split()
        log_message(console_widget, f"Parsing tokens: {tokens}", 'INFO')
        
        warnings = CSVHandler.validate_tokens_against_grammar(tokens, transformed_grammar.terminals)
        for warning in warnings:
            log_message(console_widget, warning, 'WARNING')
        
        success, trace, error = parser.parse(tokens)
        
        if success:
            log_message(console_widget, "✓ Parse SUCCESSFUL - Input ACCEPTED", 'SUCCESS')
            visualizer.draw_parse_result_indicator(result_canvas, True, THEME)
        else:
            log_message(console_widget, f"✗ Parse FAILED - Input REJECTED: {error}", 'ERROR')
            visualizer.draw_parse_result_indicator(result_canvas, False, THEME)
        
        display_trace(trace, len(trace) - 1, trace_text)
        
        return trace
    
    except Exception as e:
        log_message(console_widget, f"Error during parsing: {str(e)}", 'ERROR')
        messagebox.showerror("Error", f"Parse failed:\n{str(e)}")
        return None

def display_trace(trace, step_num, trace_text):
    """Display parse trace with enhanced formatting."""
    if not trace:
        return
    
    trace_text.delete('1.0', tk.END)
    
    trace_text.tag_config('step_header', foreground=THEME['gold'], font=('Courier', 10, 'bold'))
    trace_text.tag_config('key', foreground='#87CEEB', font=('Courier', 9, 'bold'))
    trace_text.tag_config('value', foreground=THEME['text'], font=('Courier', 9))
    
    for i in range(min(step_num + 1, len(trace))):
        step = trace[i]
        trace_text.insert(tk.END, f"╔═══ Step {i + 1} ═══╗\n", 'step_header')
        
        for key, value in step.items():
            if isinstance(value, list):
                value = ' '.join(str(v) for v in value)
            trace_text.insert(tk.END, f"{key}: ", 'key')
            trace_text.insert(tk.END, f"{value}\n", 'value')
        
        trace_text.insert(tk.END, "\n", 'value')
    
    trace_text.see(tk.END)

def main():
    """Main entry point."""
    root = create_root_window()
    root.title("⚜ Parsing Phase Tool ⚜")
    root.geometry("1600x950")
    
    setup_styles()
    
    # State variables
    state = {
        'grammar': None,
        'transformed_grammar': None,
        'parser': None,
        'current_technique': 'LL(1)',
        'parse_trace': [],
        'current_step': 0
    }
    
    # Main container
    main_container = ttk.Frame(root, style='TFrame', padding="20")
    main_container.pack(fill=tk.BOTH, expand=True)
    
    # Header
    header_frame = ttk.Frame(main_container, style='TFrame')
    header_frame.pack(fill=tk.X, pady=(0, 20))
    
    header = ttk.Label(header_frame, text="⚜ PARSING PHASE ANALYZER ⚜",
                      style='Header.TLabel')
    header.pack()
    
    subtitle = ttk.Label(header_frame, text="Grammar Analysis & Visualization",
                        font=('Georgia', 12, 'italic'), foreground=THEME['gold'],
                        background=THEME['bg'])
    subtitle.pack()
    
    # Control panel
    control_frame = ttk.Frame(main_container, style='Panel.TFrame', padding="15")
    control_frame.pack(fill=tk.X, pady=(0, 15))
    
    # Technique selection (LL(1), LR(0), SLR(1) ONLY - NO BACKTRACKING)
    technique_container = ttk.Frame(control_frame, style='Panel.TFrame')
    technique_container.pack(side=tk.LEFT, padx=10)
    
    ttk.Label(technique_container, text="Parsing Technique:",
             style='Info.TLabel').pack(side=tk.LEFT, padx=5)
    
    technique_var = tk.StringVar(value="LL(1)")
    technique_menu = ttk.Combobox(technique_container, textvariable=technique_var,
                                  values=["LL(1)", "LR(0)", "SLR(1)"],
                                  state='readonly', width=12, font=('Arial', 11))
    technique_menu.pack(side=tk.LEFT, padx=5)
    
    def on_technique_changed(event=None):
        state['current_technique'] = technique_var.get()
        state['parser'] = None
        log_message(console_widget, f"Technique changed to: {state['current_technique']}", 'INFO')
    
    technique_menu.bind('<<ComboboxSelected>>', on_technique_changed)
    
    # Buttons
    button_container = ttk.Frame(control_frame, style='Panel.TFrame')
    button_container.pack(side=tk.LEFT, padx=20)
    
    def build_parser_click():
        try:
            grammar_text = grammar_text_widget.get('1.0', tk.END).strip()
            state['grammar'] = parse_grammar(grammar_text)
            
            is_valid, issues = validate_grammar(state['grammar'])
            for issue in issues:
                level = 'WARNING' if 'Warning' in issue else 'ERROR'
                log_message(console_widget, issue, level)
            
            log_message(console_widget, "Grammar parsed successfully", 'SUCCESS')
            log_message(console_widget, f"Nonterminals: {state['grammar'].nonterminals}", 'INFO')
            log_message(console_widget, f"Terminals: {state['grammar'].terminals}", 'INFO')
            
            technique = state['current_technique']
            
            if technique == "LL(1)":
                state['parser'], state['transformed_grammar'] = build_ll1_parser(
                    state['grammar'], console_widget)
                display_ll1_results(state['parser'], state['grammar'],
                                   state['transformed_grammar'], tables_text)
            
            elif technique in ["LR(0)", "SLR(1)"]:
                state['parser'], state['transformed_grammar'] = build_lr_parser(
                    state['grammar'], technique, console_widget)
                display_lr_results(state['parser'], state['transformed_grammar'],
                                  tables_text, dfa_canvas)
        
        except Exception as e:
            log_message(console_widget, f"Error building parser: {str(e)}", 'ERROR')
            messagebox.showerror("Error", f"Failed to build parser:\n{str(e)}")
    
    def parse_tokens_click():
        tokens_str = token_entry.get().strip()
        state['parse_trace'] = parse_tokens_handler(
            state['parser'], state['transformed_grammar'], tokens_str,
            console_widget, trace_text, result_canvas)
        state['current_step'] = 0
        update_step_label()
    
    def load_csv_click():
        filename = filedialog.askopenfilename(
            title="Load Token CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'r') as f:
                content = f.read()
            
            tokens, full_data, error = CSVHandler.import_tokens(content)
            
            if error:
                messagebox.showerror("Error", error)
                return
            
            token_entry.delete(0, tk.END)
            token_entry.insert(0, ' '.join(tokens))
            log_message(console_widget, f"Loaded {len(tokens)} tokens from CSV", 'SUCCESS')
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV:\n{str(e)}")
    
    def export_results_click():
        if not state['parser']:
            messagebox.showwarning("Warning", "No parser results to export")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Export Results",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv")]
        )
        
        if not filename:
            return
        
        try:
            if filename.endswith('.json'):
                data = {
                    'technique': state['current_technique'],
                    'grammar': str(state['grammar']),
                    'trace': state['parse_trace']
                }
                
                if isinstance(state['parser'], LL1Parser):
                    data['first_sets'] = {k: list(v) for k, v in state['parser'].first_sets.items()}
                    data['follow_sets'] = {k: list(v) for k, v in state['parser'].follow_sets.items()}
                
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
            
            elif filename.endswith('.csv'):
                csv_content = CSVHandler.export_trace(state['parse_trace'])
                with open(filename, 'w') as f:
                    f.write(csv_content)
            
            log_message(console_widget, f"Results exported successfully", 'SUCCESS')
            messagebox.showinfo("Success", f"Results exported to:\n{filename}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Export failed:\n{str(e)}")
    
    ttk.Button(button_container, text="🔨 Build Parser", style='Gold.TButton',
              command=build_parser_click).pack(side=tk.LEFT, padx=5)
    
    ttk.Button(button_container, text="▶ Parse", style='Gold.TButton',
              command=parse_tokens_click).pack(side=tk.LEFT, padx=5)
    
    ttk.Button(button_container, text="📂 Load CSV",
              command=load_csv_click).pack(side=tk.LEFT, padx=5)
    
    ttk.Button(button_container, text="💾 Export",
              command=export_results_click).pack(side=tk.LEFT, padx=5)
    
    # Main content area
    content_paned = ttk.PanedWindow(main_container, orient=tk.HORIZONTAL)
    content_paned.pack(fill=tk.BOTH, expand=True)
    
    # LEFT PANEL
    left_panel = ttk.Frame(content_paned, style='Panel.TFrame', padding="15")
    content_paned.add(left_panel, weight=1)
    
    # Grammar section
    ttk.Label(left_panel, text="📝 Grammar Definition", style='Section.TLabel').pack(anchor=tk.W, pady=(0, 10))
    
    grammar_frame = tk.Frame(left_panel, bg=THEME['panel_bg'])
    grammar_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
    
    grammar_text_widget = scrolledtext.ScrolledText(
        grammar_frame, width=45, height=12,
        bg=THEME['milky'],
        fg=THEME['black'],
        font=('Courier New', 11),
        insertbackground=THEME['gold'],
        wrap=tk.WORD,
        relief=tk.FLAT,
        borderwidth=2
    )
    grammar_text_widget.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
    grammar_text_widget.insert('1.0', DEFAULT_GRAMMAR)
    
    # Token input section
    ttk.Label(left_panel, text="🎯 Input Tokens", style='Section.TLabel').pack(anchor=tk.W, pady=(10, 10))
    
    token_frame = tk.Frame(left_panel, bg=THEME['gold'], relief=tk.FLAT, borderwidth=2)
    token_frame.pack(fill=tk.X, pady=(0, 15))
    
    token_entry = tk.Entry(
        token_frame,
        font=('Courier New', 12, 'bold'),
        bg=THEME['milky'],
        fg=THEME['black'],
        insertbackground=THEME['gold'],
        relief=tk.FLAT,
        borderwidth=0
    )
    token_entry.pack(fill=tk.X, padx=2, pady=2)
    token_entry.insert(0, "int + int * int")
    
    # Parse result indicator
    result_canvas = tk.Canvas(
        left_panel,
        width=380,
        height=80,
        bg=THEME['panel_bg'],
        highlightthickness=0
    )
    result_canvas.pack(fill=tk.X, pady=(0, 15))
    
    # Console section
    ttk.Label(left_panel, text="📡 Console Log", style='Section.TLabel').pack(anchor=tk.W, pady=(0, 10))
    
    console_frame = tk.Frame(left_panel, bg=THEME['gold'], relief=tk.FLAT, borderwidth=2)
    console_frame.pack(fill=tk.BOTH, expand=True)
    
    console_widget = scrolledtext.ScrolledText(
        console_frame, width=45, height=18,
        bg=THEME['black'],
        fg=THEME['gold'],
        font=('Courier', 9),
        insertbackground=THEME['gold'],
        wrap=tk.WORD,
        relief=tk.FLAT,
        borderwidth=0
    )
    console_widget.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
    
    # RIGHT PANEL
    right_panel = ttk.Frame(content_paned, style='Panel.TFrame', padding="15")
    content_paned.add(right_panel, weight=2)
    
    # Notebook for tabs
    notebook = ttk.Notebook(right_panel)
    notebook.pack(fill=tk.BOTH, expand=True)
    
    # Tables Tab
    tables_frame = tk.Frame(notebook, bg=THEME['panel_bg'])
    notebook.add(tables_frame, text="📊 Analysis Tables")
    
    tables_text = scrolledtext.ScrolledText(
        tables_frame, width=70, height=35,
        bg=THEME['black'],
        fg=THEME['text'],
        font=('Courier', 9),
        insertbackground=THEME['gold'],
        wrap=tk.WORD,
        relief=tk.FLAT
    )
    tables_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # DFA Tab
    dfa_frame = tk.Frame(notebook, bg=THEME['panel_bg'])
    notebook.add(dfa_frame, text="🔄 DFA Visualization")
    
    dfa_canvas = tk.Canvas(
        dfa_frame, width=900, height=650,
        bg=THEME['milky'],
        highlightthickness=2,
        highlightbackground=THEME['gold']
    )
    dfa_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Trace Tab
    trace_frame = tk.Frame(notebook, bg=THEME['panel_bg'])
    notebook.add(trace_frame, text="📜 Parse Trace")
    
    trace_control = ttk.Frame(trace_frame, style='Panel.TFrame', padding="10")
    trace_control.pack(fill=tk.X)
    
    def prev_step():
        if state['current_step'] > 0:
            state['current_step'] -= 1
            display_trace(state['parse_trace'], state['current_step'], trace_text)
            update_step_label()
    
    def next_step():
        if state['parse_trace'] and state['current_step'] < len(state['parse_trace']) - 1:
            state['current_step'] += 1
            display_trace(state['parse_trace'], state['current_step'], trace_text)
            update_step_label()
    
    def update_step_label():
        total = len(state['parse_trace'])
        current = state['current_step'] + 1 if total > 0 else 0
        step_label.config(text=f"Step {current} / {total}")
    
    ttk.Button(trace_control, text="◀◀ Previous", command=prev_step).pack(side=tk.LEFT, padx=5)
    ttk.Button(trace_control, text="Next ▶▶", command=next_step).pack(side=tk.LEFT, padx=5)
    
    step_label = ttk.Label(trace_control, text="Step 0 / 0",
                           font=('Arial', 11, 'bold'),
                           foreground=THEME['gold'],
                           background=THEME['panel_bg'])
    step_label.pack(side=tk.LEFT, padx=20)
    
    trace_text = scrolledtext.ScrolledText(
        trace_frame, width=70, height=30,
        bg=THEME['black'],
        fg=THEME['text'],
        font=('Courier', 9),
        insertbackground=THEME['gold'],
        wrap=tk.WORD,
        relief=tk.FLAT
    )
    trace_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Initial log
    log_message(console_widget, "═" * 50, 'INFO')
    log_message(console_widget, "⚜ Parsing Phase Tool Initialized ⚜", 'SUCCESS')
    log_message(console_widget, "Parsing Phase Tool", 'INFO')
    log_message(console_widget, "═" * 50, 'INFO')
    log_message(console_widget, "Default grammar loaded - Ready to parse", 'INFO')
    
    root.mainloop()

if __name__ == '__main__':
    main()
