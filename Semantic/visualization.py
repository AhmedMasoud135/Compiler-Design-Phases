import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from semantic_analyzer import SemanticAnalyzer
import json


class SemanticAnalyzerGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Semantic Analyzer with Visualization")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')

        self.analyzer = SemanticAnalyzer()

        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background='#f0f0f0')
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'), background='#e0e0e0', padding=5)
        style.configure('TButton', font=('Arial', 10), padding=5)
        style.configure('Success.TLabel', foreground='green', font=('Arial', 10, 'bold'))
        style.configure('Error.TLabel', foreground='red', font=('Arial', 10, 'bold'))

        self._create_widgets()
        self._load_example_code()

    def _create_widgets(self):

        # Main title
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        title_frame.pack(fill='x', padx=0, pady=0)
        title_frame.pack_propagate(False)

        title_label = tk.Label(
            title_frame,
            text="🔍 Semantic Analyzer & Visualizer",
            font=('Arial', 20, 'bold'),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(pady=10)

        # Main container with paned window
        main_paned = ttk.PanedWindow(self.root, orient='horizontal')
        main_paned.pack(fill='both', expand=True, padx=10, pady=10)

        # Left panel - Code input
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)

        self._create_code_input_panel(left_frame)

        # Right panel - Visualization
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=2)

        self._create_visualization_panel(right_frame)

    def _create_code_input_panel(self, parent):

        # Header
        header_frame = tk.Frame(parent, bg='#3498db', height=40)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        header_label = tk.Label(
            header_frame,
            text="Source Code Input",
            font=('Arial', 14, 'bold'),
            bg='#3498db',
            fg='white'
        )
        header_label.pack(pady=8)

        # Code editor
        editor_frame = ttk.Frame(parent)
        editor_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Line numbers
        line_frame = ttk.Frame(editor_frame)
        line_frame.pack(side='left', fill='y')

        self.line_numbers = tk.Text(
            line_frame,
            width=4,
            padx=5,
            takefocus=0,
            border=0,
            background='#f0f0f0',
            state='disabled',
            wrap='none',
            font=('Courier New', 11)
        )
        self.line_numbers.pack(fill='y')

        # Code text area
        self.code_text = scrolledtext.ScrolledText(
            editor_frame,
            wrap='none',
            font=('Courier New', 11),
            bg='#ffffff',
            fg='#000000',
            insertbackground='#000000',
            selectbackground='#add8e6',
            relief='flat',
            borderwidth=2
        )
        self.code_text.pack(side='left', fill='both', expand=True)
        self.code_text.bind('<KeyRelease>', self._update_line_numbers)
        self.code_text.bind('<MouseWheel>', self._sync_scroll)

        # Button frame
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x', padx=5, pady=10)

        analyze_btn = ttk.Button(
            button_frame,
            text="▶ Analyze Code",
            command=self._analyze_code,
            style='TButton'
        )
        analyze_btn.pack(side='left', padx=5)

        clear_btn = ttk.Button(
            button_frame,
            text="🗑 Clear",
            command=self._clear_code,
            style='TButton'
        )
        clear_btn.pack(side='left', padx=5)

        load_btn = ttk.Button(
            button_frame,
            text="📂 Load File",
            command=self._load_file,
            style='TButton'
        )
        load_btn.pack(side='left', padx=5)

        example_btn = ttk.Button(
            button_frame,
            text="📝 Load Example",
            command=self._load_example_code,
            style='TButton'
        )
        example_btn.pack(side='left', padx=5)

    def _create_visualization_panel(self, parent):

        # Header
        header_frame = tk.Frame(parent, bg='#27ae60', height=40)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        header_label = tk.Label(
            header_frame,
            text="Analysis Results & Visualization",
            font=('Arial', 14, 'bold'),
            bg='#27ae60',
            fg='white'
        )
        header_label.pack(pady=8)

        # Notebook for tabs
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # Tab 1: AST Visualization
        self.ast_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.ast_tab, text='🌳 AST Tree')
        self._create_ast_tab(self.ast_tab)

        # Tab 2: Symbol Table
        self.symbol_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.symbol_tab, text='📋 Symbol Table')
        self._create_symbol_table_tab(self.symbol_tab)

        # Tab 3: Errors & Warnings
        self.errors_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.errors_tab, text='⚠️ Errors & Warnings')
        self._create_errors_tab(self.errors_tab)

        # Tab 4: Summary
        self.summary_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.summary_tab, text='📊 Summary')
        self._create_summary_tab(self.summary_tab)

    def _create_ast_tab(self, parent):

        # Canvas with scrollbars
        canvas_frame = ttk.Frame(parent)
        canvas_frame.pack(fill='both', expand=True)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient='vertical')
        v_scrollbar.pack(side='right', fill='y')

        h_scrollbar = ttk.Scrollbar(canvas_frame, orient='horizontal')
        h_scrollbar.pack(side='bottom', fill='x')

        # Canvas
        self.ast_canvas = tk.Canvas(
            canvas_frame,
            bg='white',
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        self.ast_canvas.pack(side='left', fill='both', expand=True)

        v_scrollbar.config(command=self.ast_canvas.yview)
        h_scrollbar.config(command=self.ast_canvas.xview)

        # Button frame
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill='x', pady=5)

        export_btn = ttk.Button(
            btn_frame,
            text="💾 Export AST (JSON)",
            command=self._export_ast
        )
        export_btn.pack(side='left', padx=5)

        zoom_in_btn = ttk.Button(
            btn_frame,
            text="🔍+ Zoom In",
            command=self._zoom_in
        )
        zoom_in_btn.pack(side='left', padx=5)

        zoom_out_btn = ttk.Button(
            btn_frame,
            text="🔍- Zoom Out",
            command=self._zoom_out
        )
        zoom_out_btn.pack(side='left', padx=5)

        # Zoom level
        self.zoom_level = 1.0

    def _create_symbol_table_tab(self, parent):

        # Treeview for symbol table
        columns = ('Name', 'Type', 'Scope', 'Initialized', 'Kind', 'Line')

        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Scrollbars
        v_scroll = ttk.Scrollbar(tree_frame, orient='vertical')
        v_scroll.pack(side='right', fill='y')

        h_scroll = ttk.Scrollbar(tree_frame, orient='horizontal')
        h_scroll.pack(side='bottom', fill='x')

        self.symbol_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            yscrollcommand=v_scroll.set,
            xscrollcommand=h_scroll.set
        )

        v_scroll.config(command=self.symbol_tree.yview)
        h_scroll.config(command=self.symbol_tree.xview)

        # Column headers
        for col in columns:
            self.symbol_tree.heading(col, text=col)
            self.symbol_tree.column(col, width=120, anchor='center')

        self.symbol_tree.pack(side='left', fill='both', expand=True)

        # Tags for styling
        self.symbol_tree.tag_configure('function', background='#e8f5e9')
        self.symbol_tree.tag_configure('variable', background='#e3f2fd')
        self.symbol_tree.tag_configure('uninitialized', foreground='#ff6b6b')

    def _create_errors_tab(self, parent):

        # Error section
        error_label = ttk.Label(parent, text="❌ Errors:", font=('Arial', 12, 'bold'))
        error_label.pack(anchor='w', padx=10, pady=(10, 5))

        self.errors_text = scrolledtext.ScrolledText(
            parent,
            height=10,
            wrap='word',
            font=('Courier New', 10),
            bg='#ffebee',
            fg='#c62828'
        )
        self.errors_text.pack(fill='both', expand=True, padx=10, pady=5)

        # Warning section
        warning_label = ttk.Label(parent, text="⚠️ Warnings:", font=('Arial', 12, 'bold'))
        warning_label.pack(anchor='w', padx=10, pady=(10, 5))

        self.warnings_text = scrolledtext.ScrolledText(
            parent,
            height=10,
            wrap='word',
            font=('Courier New', 10),
            bg='#fff3e0',
            fg='#f57c00'
        )
        self.warnings_text.pack(fill='both', expand=True, padx=10, pady=5)

    def _create_summary_tab(self, parent):

        # Summary frame with grid
        summary_frame = ttk.Frame(parent, padding=20)
        summary_frame.pack(fill='both', expand=True)

        # Statistics labels
        self.stats_labels = {}

        stats = [
            ('Total Lines', 'lines'),
            ('Declarations', 'declarations'),
            ('Assignments', 'assignments'),
            ('Function Calls', 'function_calls'),
            ('Errors', 'errors'),
            ('Warnings', 'warnings')
        ]

        for i, (label, key) in enumerate(stats):
            # Label
            lbl = tk.Label(
                summary_frame,
                text=f"{label}:",
                font=('Arial', 12, 'bold'),
                bg='#f0f0f0',
                anchor='w'
            )
            lbl.grid(row=i, column=0, sticky='w', padx=20, pady=10)

            # Value
            value_lbl = tk.Label(
                summary_frame,
                text="0",
                font=('Arial', 12),
                bg='#f0f0f0',
                anchor='e'
            )
            value_lbl.grid(row=i, column=1, sticky='e', padx=20, pady=10)

            self.stats_labels[key] = value_lbl

        # Status label
        self.status_label = tk.Label(
            summary_frame,
            text="✓ Ready to analyze",
            font=('Arial', 14, 'bold'),
            bg='#f0f0f0',
            fg='#27ae60'
        )
        self.status_label.grid(row=len(stats), column=0, columnspan=2, pady=30)

    def _update_line_numbers(self, event=None):
        lines = self.code_text.get('1.0', 'end-1c').split('\n')
        line_numbers_string = '\n'.join(str(i) for i in range(1, len(lines) + 1))

        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', 'end')
        self.line_numbers.insert('1.0', line_numbers_string)
        self.line_numbers.config(state='disabled')

    def _sync_scroll(self, event):
        self.line_numbers.yview_moveto(self.code_text.yview()[0])

    def _analyze_code(self):
        source_code = self.code_text.get('1.0', 'end-1c')

        if not source_code.strip():
            messagebox.showwarning("Empty Code", "Please enter some code to analyze.")
            return

        # Perform analysis
        ast, errors, warnings = self.analyzer.analyze(source_code)

        # Update all visualizations
        self._draw_ast(ast)
        self._update_symbol_table()
        self._update_errors(errors, warnings)
        self._update_summary(source_code, errors, warnings)

        # Show completion message
        if errors:
            messagebox.showinfo(
                "Analysis Complete",
                f"Analysis completed with {len(errors)} error(s) and {len(warnings)} warning(s)."
            )
        else:
            messagebox.showinfo(
                "Analysis Complete",
                f"✓ Analysis completed successfully!\n{len(warnings)} warning(s) found."
            )

    def _draw_ast(self, ast):
        self.ast_canvas.delete('all')

        if not ast:
            self.ast_canvas.create_text(
                400, 300,
                text="No AST to display",
                font=('Arial', 14),
                fill='gray'
            )
            return

        # Calculate tree layout
        self.node_width = int(120 * self.zoom_level)
        self.node_height = int(60 * self.zoom_level)
        self.level_height = int(100 * self.zoom_level)
        self.h_spacing = int(20 * self.zoom_level)

        # Calculate initial width based on tree size
        initial_width = self._calculate_tree_width(ast)

        # Draw tree starting from root
        start_x = max(400, initial_width // 2)
        self._draw_node(ast, start_x, 50, 0, initial_width)

        # Update scroll region
        bbox = self.ast_canvas.bbox('all')
        if bbox:
            # Add padding to scroll region
            padding = 50
            self.ast_canvas.config(scrollregion=(
                bbox[0] - padding,
                bbox[1] - padding,
                bbox[2] + padding,
                bbox[3] + padding
            ))

    def _calculate_tree_width(self, node, level=0):
        if not node or not node.get('children'):
            return self.node_width + self.h_spacing

        children_width = sum(self._calculate_tree_width(child, level + 1) 
                            for child in node['children'])
        return max(self.node_width + self.h_spacing, children_width)

    def _draw_node(self, node, x, y, level, width):

        if not node:
            return

        # Color scheme based on node type
        colors = {
            'program': '#3498db',
            'declaration': '#27ae60',
            'assignment': '#e74c3c',
            'binary_op': '#f39c12',
            'function_decl': '#9b59b6',
            'function_call': '#e67e22',
            'identifier': '#1abc9c',
            'literal': '#95a5a6',
            'expression': '#34495e'
        }

        # Get node type from dictionary
        node_type = node.get('node_type', 'unknown')
        color = colors.get(node_type, '#bdc3c7')

        # Draw node rectangle
        x1 = x - self.node_width // 2
        y1 = y - self.node_height // 2
        x2 = x + self.node_width // 2
        y2 = y + self.node_height // 2

        self.ast_canvas.create_rectangle(
            x1, y1, x2, y2,
            fill=color,
            outline='black',
            width=2,
            tags='node'
        )

        # Draw node text
        node_text = f"{node_type}\n"
        if node.get('value'):
            value_str = str(node['value'])
            if len(value_str) > 15:
                value_str = value_str[:12] + "..."
            node_text += f"{value_str}"

        data_type = node.get('data_type', 'unknown')
        if data_type != 'unknown':
            node_text += f"\n({data_type})"

        font_size = max(7, int(9 * self.zoom_level))
        self.ast_canvas.create_text(
            x, y,
            text=node_text,
            font=('Arial', font_size, 'bold'),
            fill='white',
            width=self.node_width - 10,
            tags='text'
        )

        # Draw children
        children = node.get('children', [])
        if children:
            child_count = len(children)
            child_y = y + self.level_height

            # Calculate spacing for children
            if child_count == 1:
                # Single child: center below parent
                child_positions = [x]
            else:
                # Multiple children: distribute horizontally
                total_width = width * 0.8
                spacing = total_width / (child_count - 1)
                start_x = x - total_width / 2
                child_positions = [start_x + i * spacing for i in range(child_count)]

            for i, child in enumerate(children):
                child_x = child_positions[i]

                # Draw line to child
                self.ast_canvas.create_line(
                    x, y2, child_x, child_y - self.node_height // 2,
                    fill='black',
                    width=max(1, int(2 * self.zoom_level)),
                    arrow='last',
                    tags='edge'
                )

                # Recursively draw child
                child_width = width / max(child_count, 1)
                self._draw_node(child, child_x, child_y, level + 1, child_width)

    def _zoom_in(self):
        self.zoom_level = min(2.0, self.zoom_level + 0.2)
        if self.analyzer.ast:
            self._draw_ast(self.analyzer.ast)

    def _zoom_out(self):
        self.zoom_level = max(0.4, self.zoom_level - 0.2)
        if self.analyzer.ast:
            self._draw_ast(self.analyzer.ast)

    def _update_symbol_table(self):
        # Clear existing items
        for item in self.symbol_tree.get_children():
            self.symbol_tree.delete(item)

        # Get symbol table info
        symbols = self.analyzer.get_symbol_table_info()

        # Add symbols to tree
        for symbol in symbols:
            kind = 'Function' if symbol['is_function'] else 'Variable'
            init_status = '✓' if symbol['initialized'] else '✗'

            tags = []
            if symbol['is_function']:
                tags.append('function')
            else:
                tags.append('variable')
                if not symbol['initialized']:
                    tags.append('uninitialized')

            self.symbol_tree.insert(
                '',
                'end',
                values=(
                    symbol['name'],
                    symbol['type'],
                    symbol['scope'],
                    init_status,
                    kind,
                    symbol['line']
                ),
                tags=tuple(tags)
            )

    def _update_errors(self, errors, warnings):
        # Clear existing
        self.errors_text.delete('1.0', 'end')
        self.warnings_text.delete('1.0', 'end')

        # Add errors
        if errors:
            for i, error in enumerate(errors, 1):
                self.errors_text.insert(
                    'end',
                    f"{i}. Line {error['line_number']}: [{error['error_type']}]\n"
                    f"   {error['message']}\n\n"
                )
        else:
            self.errors_text.insert('end', "✓ No errors found!\n")

        # Add warnings
        if warnings:
            for i, warning in enumerate(warnings, 1):
                self.warnings_text.insert(
                    'end',
                    f"{i}. Line {warning['line_number']}: [{warning['error_type']}]\n"
                    f"   {warning['message']}\n\n"
                )
        else:
            self.warnings_text.insert('end', "✓ No warnings!\n")

    def _update_summary(self, source_code, errors, warnings):
        lines = [l for l in source_code.split('\n') if l.strip()]

        # Count different statement types
        declarations = sum(1 for l in lines if any(t in l for t in ['int ', 'float ', 'string ', 'bool ']))
        assignments = sum(1 for l in lines if '=' in l and not any(t in l for t in ['int ', 'float ', 'string ', 'bool ']))
        function_calls = sum(1 for l in lines if '(' in l and ')' in l and ';' in l)

        # Update labels
        self.stats_labels['lines'].config(text=str(len(lines)))
        self.stats_labels['declarations'].config(text=str(declarations))
        self.stats_labels['assignments'].config(text=str(assignments))
        self.stats_labels['function_calls'].config(text=str(function_calls))
        self.stats_labels['errors'].config(text=str(len(errors)))
        self.stats_labels['warnings'].config(text=str(len(warnings)))

        # Update status
        if errors:
            self.status_label.config(
                text=f"✗ Analysis completed with {len(errors)} error(s)",
                fg='#e74c3c'
            )
        else:
            self.status_label.config(
                text="✓ Analysis successful!",
                fg='#27ae60'
            )

    def _export_ast(self):
        if not self.analyzer.ast:
            messagebox.showwarning("No AST", "No AST available to export.")
            return

        ast_data = self.analyzer.get_ast_structure()

        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filename:
            with open(filename, 'w') as f:
                json.dump(ast_data, f, indent=2)
            messagebox.showinfo("Export Successful", f"AST exported to {filename}")

    def _clear_code(self):
        self.code_text.delete('1.0', 'end')
        self._update_line_numbers()

        self.ast_canvas.delete('all')
        for item in self.symbol_tree.get_children():
            self.symbol_tree.delete(item)
        self.errors_text.delete('1.0', 'end')
        self.warnings_text.delete('1.0', 'end')

    def _load_file(self):
        filename = filedialog.askopenfilename(
            title="Open Source Code",
            filetypes=[
                ("Text files", "*.txt"),
                ("C files", "*.c"),
                ("All files", "*.*")
            ]
        )

        if filename:
            try:
                with open(filename, 'r') as f:
                    code = f.read()
                self.code_text.delete('1.0', 'end')
                self.code_text.insert('1.0', code)
                self._update_line_numbers()
                messagebox.showinfo("File Loaded", f"Loaded: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")

    def _load_example_code(self):
        example = """int x;
int y = 10;
float z = 3.14;
x = y + 5;
string name = "test";
bool flag = true;
int add(int a, int b)
add(x, y);
int result = x + z;
float calculate(float val)
calculate(z);"""

        self.code_text.delete('1.0', 'end')
        self.code_text.insert('1.0', example)
        self._update_line_numbers()


def main():
    root = tk.Tk()
    app = SemanticAnalyzerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()