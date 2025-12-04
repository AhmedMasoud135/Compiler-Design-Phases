import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox, Menu
from pathlib import Path
import csv
import json
from datetime import datetime

# Import your actual tokenizer functions
from main import tokenize, tokenize_file

# Enhanced color mapping for token types
TOKEN_COLORS = {
    "KEYWORD": {"foreground": "#0066CC", "background": "#E6F3FF", "font": ("Consolas", 10, "bold")},
    "IDENT": {"foreground": "#2E8B57", "background": "#F0FFF0", "font": ("Consolas", 10, "normal")},
    "LITERAL": {"foreground": "#D2691E", "background": "#FFF8DC", "font": ("Consolas", 10, "normal")},
    "OP": {"foreground": "#DC143C", "background": "#FFE4E1", "font": ("Consolas", 10, "bold")},
    "DELIMITER": {"foreground": "#4169E1", "background": "#F0F8FF", "font": ("Consolas", 10, "bold")},
    "SINGLE_COMMENT": {"foreground": "#708090", "background": "#F5F5F5", "font": ("Consolas", 10, "italic")},
    "MULTI_COMMENT": {"foreground": "#708090", "background": "#F5F5F5", "font": ("Consolas", 10, "italic")},
    "MISMATCH": {"foreground": "#FF0000", "background": "#FFD6D6", "font": ("Consolas", 10, "bold")}
}

# Statistics for different token types
TOKEN_STATS = {
    "KEYWORD": "Keywords",
    "IDENT": "Identifiers",
    "LITERAL": "Literals",
    "OP": "Operators",
    "DELIMITER": "Delimiters",
    "SINGLE_COMMENT": "Single-line comments",
    "MULTI_COMMENT": "Multi-line comments",
    "MISMATCH": "Unrecognized tokens"
}


class LexerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced C++ Lexer Analyzer")
        self.root.geometry("1400x800")
        self.root.state('zoomed') if self.root.tk.call('tk', 'windowingsystem') == 'win32' else None
        
        # Initialize variables
        self.tokens = []
        self.filtered_tokens = []
        self.current_file = None
        
        # Create menu bar
        self.create_menu()
        
        # Create main interface
        self.create_widgets()
        
        # Bind events
        self.bind_events()
        
        # Set initial state
        self.update_stats()

    def create_menu(self):
        """Create menu bar"""
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open File", accelerator="Ctrl+O", command=self.upload_file)
        file_menu.add_command(label="Save Tokens as CSV", accelerator="Ctrl+S", command=self.export_csv)
        file_menu.add_command(label="Save Tokens as JSON", command=self.export_json)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", accelerator="Ctrl+Q", command=self.root.quit)
        
        # Edit menu
        edit_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Clear All", accelerator="Ctrl+L", command=self.clear_all)
        edit_menu.add_command(label="Find Token", accelerator="Ctrl+F", command=self.find_token)
        
        # View menu
        view_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Expand All", command=self.expand_code_editor)
        view_menu.add_command(label="Show Statistics", command=self.show_detailed_stats)

    def create_widgets(self):
        """Create main interface widgets"""
        # Main container with notebook for tabs
        self.notebook = tb.Notebook(self.root)
        self.notebook.pack(fill=BOTH, expand=True, padx=10, pady=5)
        
        # Main analysis tab
        self.main_frame = tb.Frame(self.notebook)
        self.notebook.add(self.main_frame, text="Lexical Analysis")
        
        # Statistics tab
        self.stats_frame = tb.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Statistics")
        
        self.create_main_tab()
        self.create_stats_tab()

    def create_main_tab(self):
        """Create main analysis tab"""
        # Top toolbar
        toolbar = tb.Frame(self.main_frame, padding=5)
        toolbar.pack(fill=X)
        
        # File info label
        self.file_info_label = tb.Label(toolbar, text="No file loaded", font=("Arial", 10))
        self.file_info_label.pack(side=LEFT)
        
        # Buttons
        btn_frame = tb.Frame(toolbar)
        btn_frame.pack(side=RIGHT)
        
        self.lex_btn = tb.Button(btn_frame, text="🔍 Analyze Code", bootstyle=SUCCESS, 
                                command=self.lex_code, width=15)
        self.lex_btn.pack(side=LEFT, padx=2)
        
        self.upload_btn = tb.Button(btn_frame, text="📁 Upload File", bootstyle=INFO, 
                                   command=self.upload_file, width=15)
        self.upload_btn.pack(side=LEFT, padx=2)
        
        self.export_btn = tb.Button(btn_frame, text="💾 Export CSV", bootstyle=PRIMARY, 
                                   command=self.export_csv, width=15)
        self.export_btn.pack(side=LEFT, padx=2)
        
        self.clear_btn = tb.Button(btn_frame, text="🗑️ Clear", bootstyle=DANGER, 
                                  command=self.clear_all, width=15)
        self.clear_btn.pack(side=LEFT, padx=2)
        
        # Main paned window
        self.paned = tb.PanedWindow(self.main_frame, orient=HORIZONTAL)
        self.paned.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # Left panel: Code editor
        self.create_code_editor()
        
        # Right panel: Token analysis
        self.create_token_panel()

    def create_code_editor(self):
        """Create code editor panel"""
        editor_frame = tb.LabelFrame(self.paned, text="C++ Code Editor", padding=10)
        self.paned.add(editor_frame, weight=2)
        
        # Code text area with line numbers
        text_frame = tb.Frame(editor_frame)
        text_frame.pack(fill=BOTH, expand=True)
        
        # Line numbers (simple implementation)
        self.line_numbers = tb.Text(text_frame, width=4, padx=3, takefocus=0,
                                   border=0, state='disabled', wrap='none',
                                   font=("Consolas", 10))
        self.line_numbers.pack(side=LEFT, fill=Y)
        
        # Main text area
        self.code_text = tb.Text(text_frame, font=("Consolas", 11), wrap='none',
                                undo=True, maxundo=20)
        self.code_text.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Scrollbars
        v_scrollbar = tb.Scrollbar(text_frame, orient="vertical", command=self.sync_scroll)
        v_scrollbar.pack(side=RIGHT, fill=Y)
        self.code_text.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = tb.Scrollbar(editor_frame, orient="horizontal", command=self.code_text.xview)
        h_scrollbar.pack(side=BOTTOM, fill=X)
        self.code_text.configure(xscrollcommand=h_scrollbar.set)
        
        # Sample code - using your actual C++ code format
        sample_code = """// Sample C++ Code for Lexical Analysis
#include <iostream>
using namespace std;

int main() {
    int number = 42;
    float pi = 3.14159;
    char letter = 'A';
    string message = "Hello, World!";
    
    cout << message << endl;
    cout << "Number: " << number << endl;
    
    /* Multi-line comment
       for lexical analysis demo
       testing multiple lines */
    
    if (number > 0) {
        number += 10;
        number++;
    }
    
    return 0;
}"""
        self.code_text.insert("1.0", sample_code)
        self.update_line_numbers()

    def create_token_panel(self):
        """Create token analysis panel"""
        token_frame = tb.LabelFrame(self.paned, text="Token Analysis", padding=10)
        self.paned.add(token_frame, weight=3)
        
        # Filter and search frame
        filter_frame = tb.Frame(token_frame)
        filter_frame.pack(fill=X, pady=(0, 10))
        
        # Filter dropdown
        tb.Label(filter_frame, text="Filter:", font=("Arial", 10, "bold")).pack(side=LEFT, padx=(0, 5))
        self.filter_var = tb.StringVar(value="All")
        filter_options = ["All"] + list(TOKEN_COLORS.keys())
        self.filter_dropdown = tb.Combobox(filter_frame, textvariable=self.filter_var, 
                                          values=filter_options, state="readonly", width=15)
        self.filter_dropdown.pack(side=LEFT, padx=(0, 10))
        
        # Search entry
        tb.Label(filter_frame, text="Search:", font=("Arial", 10, "bold")).pack(side=LEFT, padx=(10, 5))
        self.search_var = tb.StringVar()
        self.search_entry = tb.Entry(filter_frame, textvariable=self.search_var, width=20)
        self.search_entry.pack(side=LEFT, padx=(0, 5))
        
        self.search_btn = tb.Button(filter_frame, text="🔍", bootstyle=INFO, width=3,
                                   command=self.search_tokens)
        self.search_btn.pack(side=LEFT)
        
        # Quick stats frame
        stats_frame = tb.Frame(filter_frame)
        stats_frame.pack(side=RIGHT)
        
        self.token_count_label = tb.Label(stats_frame, text="Tokens: 0", 
                                         font=("Arial", 10, "bold"), bootstyle=INFO)
        self.token_count_label.pack(side=RIGHT, padx=10)
        
        # Token table with better styling
        table_container = tb.Frame(token_frame)
        table_container.pack(fill=BOTH, expand=True)
        
        # Treeview with custom styling
        self.token_table = tb.Treeview(table_container, 
                                      columns=("Type", "Value", "Line", "Col", "Description"),
                                      show='headings', bootstyle="info", height=20)
        
        # Configure columns
        self.token_table.heading("Type", text="Token Type", command=lambda: self.sort_table("Type"))
        self.token_table.heading("Value", text="Value", command=lambda: self.sort_table("Value"))
        self.token_table.heading("Line", text="Line", command=lambda: self.sort_table("Line"))
        self.token_table.heading("Col", text="Column", command=lambda: self.sort_table("Col"))
        self.token_table.heading("Description", text="Description")
        
        self.token_table.column("Type", width=120, anchor="center")
        self.token_table.column("Value", width=200)
        self.token_table.column("Line", width=80, anchor="center")
        self.token_table.column("Col", width=80, anchor="center")
        self.token_table.column("Description", width=250)
        
        self.token_table.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Scrollbar for table
        table_scrollbar = tb.Scrollbar(table_container, orient="vertical", 
                                      command=self.token_table.yview)
        self.token_table.configure(yscrollcommand=table_scrollbar.set)
        table_scrollbar.pack(side=RIGHT, fill=Y)

    def create_stats_tab(self):
        """Create statistics tab"""
        # Statistics overview
        overview_frame = tb.LabelFrame(self.stats_frame, text="Token Statistics Overview", padding=15)
        overview_frame.pack(fill=X, padx=10, pady=10)
        
        self.stats_text = tb.Text(overview_frame, height=10, font=("Consolas", 10), state='disabled')
        self.stats_text.pack(fill=BOTH, expand=True)
        
        # Detailed breakdown
        detail_frame = tb.LabelFrame(self.stats_frame, text="Detailed Breakdown", padding=15)
        detail_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview for detailed stats
        self.stats_tree = tb.Treeview(detail_frame, columns=("Count", "Percentage", "Examples"), 
                                     show='tree headings', bootstyle="info")
        self.stats_tree.heading("#0", text="Token Type")
        self.stats_tree.heading("Count", text="Count")
        self.stats_tree.heading("Percentage", text="Percentage")
        self.stats_tree.heading("Examples", text="Examples")
        
        self.stats_tree.column("#0", width=200)
        self.stats_tree.column("Count", width=100, anchor="center")
        self.stats_tree.column("Percentage", width=100, anchor="center")
        self.stats_tree.column("Examples", width=300)
        
        self.stats_tree.pack(fill=BOTH, expand=True)

    def bind_events(self):
        """Bind keyboard and mouse events"""
        # Keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self.upload_file())
        self.root.bind('<Control-s>', lambda e: self.export_csv())
        self.root.bind('<Control-l>', lambda e: self.clear_all())
        self.root.bind('<Control-f>', lambda e: self.find_token())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        
        # Text events
        self.code_text.bind('<KeyRelease>', self.on_text_change)
        self.code_text.bind('<Button-1>', self.on_text_change)
        self.code_text.bind('<MouseWheel>', self.on_text_change)
        
        # Filter and search events
        self.filter_dropdown.bind("<<ComboboxSelected>>", self.apply_filter)
        self.search_var.trace('w', self.on_search_change)
        self.search_entry.bind('<Return>', lambda e: self.search_tokens())
        
        # Table events
        self.token_table.bind('<Double-1>', self.on_token_double_click)
        self.token_table.bind('<Button-3>', self.show_context_menu)

    def sync_scroll(self, *args):
        """Synchronize scrolling between text and line numbers"""
        self.code_text.yview(*args)
        self.line_numbers.yview(*args)

    def update_line_numbers(self, event=None):
        """Update line numbers"""
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', 'end')
        
        content = self.code_text.get('1.0', 'end-1c')
        lines = content.split('\n')
        line_numbers = '\n'.join(str(i) for i in range(1, len(lines) + 1))
        
        self.line_numbers.insert('1.0', line_numbers)
        self.line_numbers.config(state='disabled')

    def on_text_change(self, event=None):
        """Handle text changes"""
        self.root.after_idle(self.update_line_numbers)

    def lex_code(self):
        """Analyze the code and extract tokens using your actual tokenizer"""
        code = self.code_text.get("1.0", "end-1c")
        if not code.strip():
            messagebox.showwarning("Warning", "Please enter some code or upload a file!")
            return
        
        try:
            # Show progress
            self.lex_btn.config(text="Analyzing...", state='disabled')
            self.root.update()
            
            # Use your actual tokenize function
            self.tokens = tokenize(code)
            self.filtered_tokens = self.tokens.copy()
            
            # Update displays
            self.show_tokens(self.tokens)
            self.update_stats()
            self.update_token_count()
            
            # Update file info
            self.file_info_label.config(text=f"Code analyzed - {len(self.tokens)} tokens found")
            
            #messagebox.showinfo("Success", f"Analysis complete! Found {len(self.tokens)} tokens.")
            
        except RuntimeError as e:
            # Handle lexical errors from your tokenizer
            messagebox.showerror("Lexical Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Error during analysis:\n{str(e)}")
        finally:
            self.lex_btn.config(text="🔍 Analyze Code", state='normal')

    def upload_file(self):
        """Upload and analyze a C++ file using your actual tokenizer"""
        filepath = filedialog.askopenfilename(
            title="Select C++ File", 
            filetypes=[("C++ Files", "*.cpp *.c *.h *.hpp"), ("All Files", "*.*")]
        )
        if filepath:
            try:
                self.current_file = filepath
                
                # Show progress
                self.upload_btn.config(text="Loading...", state='disabled')
                self.root.update()
                
                # Use your actual tokenize_file function
                self.tokens = tokenize_file(filepath)
                self.filtered_tokens = self.tokens.copy()
                
                # Load file content
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                
                self.code_text.delete("1.0", "end")
                self.code_text.insert("1.0", content)
                
                # Update displays
                self.show_tokens(self.tokens)
                self.update_stats()
                self.update_token_count()
                self.update_line_numbers()
                
                # Update file info
                filename = Path(filepath).name
                self.file_info_label.config(text=f"File: {filename} - {len(self.tokens)} tokens")
                
                messagebox.showinfo("Success", f"File loaded successfully!\nFound {len(self.tokens)} tokens.")
                
            except RuntimeError as e:
                # Handle lexical errors from your tokenizer
                messagebox.showerror("Lexical Error", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"Error loading file:\n{str(e)}")
            finally:
                self.upload_btn.config(text="📁 Upload File", state='normal')

    def show_tokens(self, tokens):
        """Display tokens in the table with proper formatting"""
        # Clear existing items
        for item in self.token_table.get_children():
            self.token_table.delete(item)
        
        # Configure tags for coloring
        for token_type, colors in TOKEN_COLORS.items():
            self.token_table.tag_configure(token_type, 
                                         foreground=colors["foreground"],
                                         background=colors["background"])
        
        # Insert tokens
        for i, token in enumerate(tokens):
            token_type = token['type']
            description = TOKEN_STATS.get(token_type, "Unknown token type")
            
            # Truncate long values for display
            display_value = token['value']
            if len(display_value) > 50:
                display_value = display_value[:47] + "..."
            
            self.token_table.insert('', 'end', 
                                  values=(token_type, display_value, token['line'], 
                                         token['col'], description),
                                  tags=(token_type,))

    def apply_filter(self, event=None):
        """Apply filter to token display - WORKING VERSION"""
        filter_value = self.filter_var.get()
        search_term = self.search_var.get().lower()
        
        # Clear current display
        for item in self.token_table.get_children():
            self.token_table.delete(item)
        
        # Filter tokens
        self.filtered_tokens = []
        for token in self.tokens:
            # Apply type filter
            if filter_value != "All" and token['type'] != filter_value:
                continue
            
            # Apply search filter
            if search_term and search_term not in token['value'].lower():
                continue
            
            self.filtered_tokens.append(token)
        
        # Display filtered tokens
        self.show_tokens(self.filtered_tokens)
        self.update_token_count()

    def on_search_change(self, *args):
        """Handle search text changes"""
        self.root.after_idle(self.apply_filter)

    def search_tokens(self):
        """Search for specific tokens"""
        self.apply_filter()

    def update_token_count(self):
        """Update token count display"""
        total = len(self.tokens)
        filtered = len(self.filtered_tokens)
        
        if total == filtered:
            self.token_count_label.config(text=f"Tokens: {total}")
        else:
            self.token_count_label.config(text=f"Tokens: {filtered}/{total}")

    def sort_table(self, column):
        """Sort table by column"""
        # Get all items
        items = [(self.token_table.item(item)['values'], item) for item in self.token_table.get_children()]
        
        # Sort by column
        col_index = {"Type": 0, "Value": 1, "Line": 2, "Col": 3}[column]
        
        if column in ["Line", "Col"]:
            # Numeric sort
            items.sort(key=lambda x: int(x[0][col_index]))
        else:
            # String sort
            items.sort(key=lambda x: str(x[0][col_index]))
        
        # Rearrange items
        for index, (values, item) in enumerate(items):
            self.token_table.move(item, '', index)

    def update_stats(self):
        """Update statistics display"""
        if not self.tokens:
            return
        
        # Count tokens by type
        token_counts = {}
        for token in self.tokens:
            token_type = token['type']
            token_counts[token_type] = token_counts.get(token_type, 0) + 1
        
        total_tokens = len(self.tokens)
        
        # Update text statistics
        self.stats_text.config(state='normal')
        self.stats_text.delete('1.0', 'end')
        
        stats_content = f"LEXICAL ANALYSIS STATISTICS\n"
        stats_content += f"{'='*50}\n\n"
        stats_content += f"Total Tokens: {total_tokens}\n"
        stats_content += f"Unique Token Types: {len(token_counts)}\n"
        stats_content += f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        stats_content += "TOKEN TYPE DISTRIBUTION:\n"
        stats_content += f"{'-'*30}\n"
        
        for token_type, count in sorted(token_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_tokens) * 100
            stats_content += f"{token_type:15} : {count:4d} ({percentage:5.1f}%)\n"
        
        self.stats_text.insert('1.0', stats_content)
        self.stats_text.config(state='disabled')
        
        # Update detailed tree
        for item in self.stats_tree.get_children():
            self.stats_tree.delete(item)
        
        for token_type, count in sorted(token_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = f"{(count / total_tokens) * 100:.1f}%"
            
            # Get examples
            examples = [t['value'] for t in self.tokens if t['type'] == token_type][:3]
            examples_str = ", ".join(examples[:3])
            if len(examples) > 3:
                examples_str += "..."
            
            self.stats_tree.insert('', 'end', text=token_type,
                                  values=(count, percentage, examples_str))

    def on_token_double_click(self, event):
        """Handle double-click on token"""
        selection = self.token_table.selection()
        if selection:
            item = self.token_table.item(selection[0])
            values = item['values']
            line_num = int(values[2])
            
            # Highlight line in code editor
            self.code_text.tag_remove('highlight', '1.0', 'end')
            start_pos = f"{line_num}.0"
            end_pos = f"{line_num}.end"
            self.code_text.tag_add('highlight', start_pos, end_pos)
            self.code_text.tag_configure('highlight', background='yellow')
            self.code_text.see(start_pos)

    def show_context_menu(self, event):
        """Show context menu for token table"""
        selection = self.token_table.selection()
        if selection:
            context_menu = Menu(self.root, tearoff=0)
            context_menu.add_command(label="Copy Value", 
                                   command=lambda: self.copy_token_value(selection[0]))
            context_menu.add_command(label="Find Similar", 
                                   command=lambda: self.find_similar_tokens(selection[0]))
            context_menu.add_separator()
            context_menu.add_command(label="Go to Line", 
                                   command=lambda: self.go_to_token_line(selection[0]))
            
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()

    def copy_token_value(self, item):
        """Copy token value to clipboard"""
        values = self.token_table.item(item)['values']
        self.root.clipboard_clear()
        self.root.clipboard_append(values[1])  # Token value

    def find_similar_tokens(self, item):
        """Find tokens of the same type"""
        values = self.token_table.item(item)['values']
        token_type = values[0]
        self.filter_var.set(token_type)
        self.apply_filter()

    def go_to_token_line(self, item):
        """Go to token line in code editor"""
        values = self.token_table.item(item)['values']
        line_num = int(values[2])
        self.code_text.mark_set('insert', f"{line_num}.0")
        self.code_text.see(f"{line_num}.0")
        self.notebook.select(0)  # Switch to main tab

    def clear_all(self):
        """Clear all data"""
        if messagebox.askyesno("Confirm", "Clear all data and start fresh?"):
            self.tokens = []
            self.filtered_tokens = []
            self.current_file = None
            
            # Clear displays
            for item in self.token_table.get_children():
                self.token_table.delete(item)
            
            self.code_text.delete("1.0", "end")
            self.stats_text.config(state='normal')
            self.stats_text.delete('1.0', 'end')
            self.stats_text.config(state='disabled')
            
            for item in self.stats_tree.get_children():
                self.stats_tree.delete(item)
            
            # Reset UI
            self.filter_var.set("All")
            self.search_var.set("")
            self.file_info_label.config(text="No file loaded")
            self.update_token_count()
            self.update_line_numbers()

    def find_token(self):
        """Open find dialog"""
        find_window = tb.Toplevel(self.root)
        find_window.title("Find Token")
        find_window.geometry("400x150")
        find_window.transient(self.root)
        find_window.grab_set()
        
        tb.Label(find_window, text="Search for token:", font=("Arial", 10)).pack(pady=10)
        
        search_entry = tb.Entry(find_window, width=30, font=("Arial", 11))
        search_entry.pack(pady=5)
        search_entry.focus()
        
        def do_search():
            search_term = search_entry.get()
            if search_term:
                self.search_var.set(search_term)
                self.apply_filter()
                find_window.destroy()
        
        btn_frame = tb.Frame(find_window)
        btn_frame.pack(pady=10)
        
        tb.Button(btn_frame, text="Search", bootstyle=SUCCESS, command=do_search).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="Cancel", bootstyle=SECONDARY, command=find_window.destroy).pack(side=LEFT, padx=5)
        
        search_entry.bind('<Return>', lambda e: do_search())

    def export_csv(self):
        """Export tokens to CSV"""
        if not self.tokens:
            messagebox.showwarning("Warning", "No tokens to export!")
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv", 
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Save Tokens as CSV"
        )
        
        if filepath:
            try:
                with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(["Type", "Value", "Line", "Column", "Description"])
                    
                    for token in self.tokens:
                        description = TOKEN_STATS.get(token['type'], "Unknown")
                        writer.writerow([token['type'], token['value'], 
                                       token['line'], token['col'], description])
                
                messagebox.showinfo("Success", f"Tokens exported to {filepath} successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Error exporting CSV:\n{str(e)}")

    def export_json(self):
        """Export tokens to JSON"""
        if not self.tokens:
            messagebox.showwarning("Warning", "No tokens to export!")
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json", 
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            title="Save Tokens as JSON"
        )
        
        if filepath:
            try:
                export_data = {
                    "metadata": {
                        "total_tokens": len(self.tokens),
                        "export_date": datetime.now().isoformat(),
                        "source_file": self.current_file
                    },
                    "tokens": self.tokens
                }
                
                with open(filepath, "w", encoding="utf-8") as jsonfile:
                    json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Success", f"Tokens exported to {filepath} successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Error exporting JSON:\n{str(e)}")

    def expand_code_editor(self):
        """Expand code editor to full window"""
        if self.paned.sash_coord(0)[0] > 100:
            self.paned.sash_place(0, 50, 0)
        else:
            self.paned.sash_place(0, 700, 0)

    def show_detailed_stats(self):
        """Show detailed statistics window"""
        if not self.tokens:
            messagebox.showinfo("Info", "No tokens to analyze!")
            return
        
        stats_window = tb.Toplevel(self.root)
        stats_window.title("Detailed Token Statistics")
        stats_window.geometry("600x500")
        stats_window.transient(self.root)
        
        # Create detailed analysis
        detail_text = tb.Text(stats_window, font=("Consolas", 10))
        detail_text.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Generate detailed statistics
        token_counts = {}
        line_counts = {}
        
        for token in self.tokens:
            token_type = token['type']
            line_num = token['line']
            
            token_counts[token_type] = token_counts.get(token_type, 0) + 1
            if line_num not in line_counts:
                line_counts[line_num] = []
            line_counts[line_num].append(token)
        
        content = "DETAILED LEXICAL ANALYSIS REPORT\n"
        content += "=" * 60 + "\n\n"
        
        content += f"Analysis Summary:\n"
        content += f"- Total tokens: {len(self.tokens)}\n"
        content += f"- Lines of code: {max(line_counts.keys()) if line_counts else 0}\n"
        content += f"- Token types: {len(token_counts)}\n\n"
        
        content += "Token Distribution:\n"
        content += "-" * 30 + "\n"
        for token_type, count in sorted(token_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(self.tokens)) * 100
            content += f"{token_type:15} : {count:4d} tokens ({percentage:5.1f}%)\n"
        
        content += "\nLine-by-Line Analysis:\n"
        content += "-" * 30 + "\n"
        for line_num in sorted(line_counts.keys())[:20]:  # Show first 20 lines
            tokens_in_line = line_counts[line_num]
            content += f"Line {line_num:3d}: {len(tokens_in_line):2d} tokens - "
            content += ", ".join([f"{t['type']}({t['value'][:10]}{'...' if len(t['value']) > 10 else ''})" 
                                for t in tokens_in_line[:5]])
            if len(tokens_in_line) > 5:
                content += "..."
            content += "\n"
        
        if len(line_counts) > 20:
            content += f"... and {len(line_counts) - 20} more lines\n"
        
        detail_text.insert('1.0', content)
        detail_text.config(state='disabled')


if __name__ == "__main__":
    # Create the application
    root = tb.Window(themename="cosmo")  # Modern theme
    app = LexerGUI(root)
    
    # Set window icon (if you have one)
    try:
        root.iconbitmap('icon.ico')  # Add your icon file
    except:
        pass
    
    # Start the application
    root.mainloop()