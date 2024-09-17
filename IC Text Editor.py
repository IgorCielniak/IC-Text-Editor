import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from tkinter.scrolledtext import ScrolledText
import os
import sys
import datetime
import re
import json
from tkinter.colorchooser import askcolor
from tkterm import Terminal


class TextEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("IC Text Editor")
        self.notebook = ttk.Notebook(self.master)
        self.master.bind('<Control-Shift-N>', lambda event: self.create_tab())
        self.master.bind('<Control-Shift-C>', lambda event: self.close_tab())
        self.master.bind('<Control-Shift-S>', lambda event: self.save_file())
        self.master.bind('<Control-Shift-D>', lambda event: self.write_date_time())
        self.master.bind('<Control-Shift-F>', lambda event: self.find_text())
        self.master.bind('<Control-Shift-O>', lambda event: self.open_file())
        self.master.bind('<Control-Shift-T>', lambda event: self.add_tab_with_table())
        self.master.bind('<Alt_L>', lambda event: self.auto_complete())
        self.text_areas = []
        terminalrelheight = 0.3
        self.pixeloffset = 93
        self.notebookpady = (root.winfo_screenheight() - self.pixeloffset) * terminalrelheight
        self.tab = 0
        self.app_dir = os.path.dirname(sys.argv[0])
        self.highlight_rules = {}
        self.highlighting = tk.IntVar(value=1)
        self.syntax_files = []
        self.load_highlight_rules(self.app_dir + "\\config.json")
        self.create_tab()
        self.tab = self.notebook.index("current")
        self.init_menu()

        self.suggestions_popup = None
        self.suggestions_listbox = None
        self.last_word = None

        self.current_text = self.text_areas[self.tab].get("1.0", tk.END).split()
        self.current_word = ""
        self.suggestions = [word for word in self.highlight_rules.keys() if word.startswith(self.current_word)]
        self.create_file_tree()
        self.notebook.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.BOTH, pady=(0, self.notebookpady))



    def on_tree_double_click(self, event):
        item = self.file_tree.selection()[0]
        file_path = self.file_tree.item(item, "text")
        full_path = os.path.join(self.file_tree.item(self.file_tree.parent(item), "text"), file_path)
        if os.path.isfile(full_path):
            self.open_file_from_tree(full_path)

    def open_file_from_tree(self, file_path):
        with open(file_path, "r") as file:
            content = file.read()
            self.create_tab()
            self.text_areas[len(self.text_areas)-1].delete("1.0", tk.END)
            self.text_areas[len(self.text_areas)-1].insert("1.0", content)
            self.notebook.tab(len(self.text_areas)-1, text=file_path)
            self.highlight_words(event=None)


    def refresh_file_tree(self):
        self.populate_tree()

    def create_file_tree(self):
        self.tree_frame = ttk.Frame(self.master)
        self.tree_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_tree = ttk.Treeview(self.tree_frame)
        self.file_tree.pack(expand=True, fill=tk.BOTH)
        
        self.file_tree.bind("<Double-1>", self.on_tree_double_click)
        
        self.populate_tree()

    def populate_tree(self):
        path = "."  # Start from the current directory
        self.file_tree.delete(*self.file_tree.get_children())
        abspath = os.path.abspath(path)
        root_node = self.file_tree.insert('', 'end', text=abspath, open=True)
        self.process_directory(root_node, abspath)

    def process_directory(self, parent, path):
        for p in os.listdir(path):
            abspath = os.path.join(path, p)
            isdir = os.path.isdir(abspath)
            oid = self.file_tree.insert(parent, 'end', text=p, open=False)
            if isdir:
                self.process_directory(oid, abspath)


    def changeBg(self):
        (triple, hexstr) = askcolor()
        if hexstr:
            self.text_area.config(bg=hexstr)

    def changeFg(self):
        (triple, hexstr) = askcolor()
        if hexstr:
            self.text_area.config(fg=hexstr)

    def find_text(self):
        text_widget = self.text_areas[self.tab]
        
        search_query = simpledialog.askstring("Find", "Enter search query:")

        if search_query:
            search_results = text_widget.search(search_query, "1.0", tk.END)
            if search_results:
                text_widget.tag_remove(tk.SEL, "1.0", tk.END)
                text_widget.tag_add(tk.SEL, search_results, f"{search_results}+{len(search_query)}c")
                text_widget.mark_set(tk.INSERT, search_results)
                text_widget.see(tk.INSERT)
                messagebox.showinfo("Info", f"Found '{search_query}' in text.")
            else:
                messagebox.showinfo("Info", f"'{search_query}' not found in text.")

    def handle_key_release(self, event):
        self.highlight_words(event)
        current_text = self.text_areas[self.tab].get("1.0", tk.END).split()
        try:
            current_word = current_text[len(current_text) - 1]
            if self.last_word == current_word:
                return
            self.last_word = current_word
            self.suggestions = [word for word in self.highlight_rules.keys() if word.startswith(current_word)]
            if self.suggestions:
                self.show_suggestions(self.suggestions)
            else:
                self.hide_suggestions()
        except IndexError:
            self.last_word = None

    def show_suggestions(self, suggestions):
        if not self.suggestions_popup:
            self.suggestions_popup = tk.Toplevel(self.master)
            self.suggestions_popup.wm_overrideredirect(True)
            self.suggestions_popup.bind('<FocusOut>', lambda event: self.hide_suggestions())
            self.suggestions_listbox = tk.Listbox(self.suggestions_popup, height=min(len(suggestions), 4))
            self.suggestions_listbox.pack()

        self.suggestions_listbox.delete(0, tk.END)
        for suggestion in suggestions:
            self.suggestions_listbox.insert(tk.END, suggestion)

        x, y, _, h = self.text_areas[self.tab].bbox(tk.INSERT)
        x += self.text_areas[self.tab].winfo_rootx() + 2
        y += self.text_areas[self.tab].winfo_rooty() + h + 2
        self.suggestions_popup.geometry(f"+{x}+{y}")
        self.suggestions_popup.deiconify()


    def hide_suggestions(self):
        if self.suggestions_popup:
            self.suggestions_popup.withdraw()

    def load_highlight_rules(self, file_path):
        try:
            with open(file_path, "r") as file:
                config_data = json.load(file)
                if "syntax_files" in config_data:
                    self.syntax_files = config_data["syntax_files"]
                    for syntax_file in self.syntax_files:
                        self.parse_syntax_file(syntax_file)
        except FileNotFoundError:
            messagebox.showwarning("Warning", f"Configuration file not found: {file_path}. No custom highlighting will be applied.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration file from {file_path}: {str(e)}")

    def parse_syntax_file(self, syntax_file):
        try:
            with open(syntax_file, "r") as file:
                for line in file:
                    if ":" in line:
                        word, color = line.strip().split(":")
                        self.highlight_rules[word.strip()] = color.strip()
        except FileNotFoundError:
            messagebox.showwarning("Warning", f"Syntax file not found: {syntax_file}. No custom highlighting will be applied.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse syntax file {syntax_file}: {str(e)}")

    def create_tab(self):
        self.text_area = ScrolledText(self.notebook, wrap=tk.WORD)
        self.text_area.bind('<KeyRelease>', self.handle_key_release)
        self.text_areas.append(self.text_area)
        self.notebook.add(self.text_area, text=f"Tab {len(self.text_areas)}")
        self.notebook.pack(expand=tk.YES, fill=tk.BOTH, pady = (0,self.notebookpady))
        self.notebook.select(self.tab)

    def close_tab(self):
        if len(self.text_areas) > 1:
            tab = self.notebook.select()
            self.notebook.forget(tab)
            self.text_areas.pop(self.tab)
            self.tab = self.notebook.select()

    def init_menu(self):
        menu = tk.Menu(self.master)
        self.master.config(menu=menu)

        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="New Tab", command=self.new_file)
        file_menu.add_command(label="Close Tab", command=self.close_tab)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.quit)
        file_menu.add_command(label="Refresh File Tree", command=self.refresh_file_tree)
        menu.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menu, tearoff=0)
        edit_menu.add_command(label="Cut", command=self.cut)
        edit_menu.add_command(label="Copy", command=self.copy)
        edit_menu.add_command(label="Paste", command=self.paste)
        edit_menu.add_command(label="Select All", command=self.select_all)
        edit_menu.add_command(label="Find Text", command=self.find_text)
        edit_menu.add_command(label="Run", command=self.run)
        menu.add_cascade(label="Edit", menu=edit_menu)

        insert_menu = tk.Menu(menu, tearoff=0)
        insert_menu.add_command(label="Table", command=self.add_tab_with_table)
        insert_menu.add_command(label="Date and time", command=self.write_date_time)
        menu.add_cascade(label="Insert", menu=insert_menu)

        settings_menu = tk.Menu(menu, tearoff=0)
        settings_menu.add_command(label="Change font size", command=self.change_font_size)
        settings_menu.add_command(label="Change font color", command=self.changeFg)
        settings_menu.add_command(label="Change background color", command=self.changeBg)
        settings_menu.add_command(label="Shortcuts", command=self.shortcuts)
        settings_menu.add_checkbutton(label="Highliting", variable = self.highlighting)
        settings_menu.add_command(label="terminal height", command = self.terminalheightfunc)
        menu.add_cascade(label="Settings", menu=settings_menu)

        about_menu = tk.Menu(menu, tearoff=0)
        about_menu.add_command(label="Info", command=self.info)
        about_menu.add_command(label="Licence", command=self.license)
        about_menu.add_command(label="Contact", command=self.contact)
        menu.add_cascade(label="About", menu=about_menu)

    def contact(self):
        messagebox.showinfo("Contact", "igorcielniak.contact@gmail.com")

    def change_font_size(self):
        text_widget = self.text_areas[self.tab]
        font_size = simpledialog.askinteger("Change font size", "Enter new font size:")
        if font_size:
            font = text_widget['font']
            font_specs = font.split()
            font_family = font_specs[0]
            text_widget.configure(font=(font_family, font_size))

    def new_file(self):
        self.create_tab()

    def readFile(self, filename):
        try:
            fn = open(filename, 'r+')
            text = fn.read()
            return text
        except:
            messagebox.showerror("Oops! Something Wrong!")
            return None

    def open_file(self):
        file_path = tk.filedialog.askopenfilename(defaultextension="*.*", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*"), ("Pryzma",  "*.pryzma"), ("Doc", "*.doc"), ("python file", "*.py"), ("rtf", "*.rtf"), ("docx", "*.docx"), ("odt", "*.odt"), ("css", "*.css"), ("HTML", "*.html"), ("xml", "*.xml"), ("wps", "*.wps"), ("java script", "*.js"), ("JSON", "*.json")])

        if file_path:
            try:
                with open(file_path, "r") as file:
                    content = file.read()
                    self.create_tab()
                    self.text_areas[len(self.text_areas)-1].delete("1.0", tk.END)
                    self.text_areas[len(self.text_areas)-1].insert("1.0", content)
                    self.notebook.tab(len(self.text_areas)-1, text=file_path)
                    self.highlight_words(event=None)
                    messagebox.showinfo("Info", f"File opened: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {str(e)}")
        

    def highlight_words(self, event):
        if self.highlighting.get() == 1:
            self.tab = self.notebook.index("current")
            text_widget = self.text_areas[self.tab]
            text_widget.tag_remove("highlight", "1.0", tk.END)
            for word, color in self.highlight_rules.items():
                start = "1.0"
                while True:
                    start = text_widget.search(word, start, stopindex=tk.END, nocase=True)
                    if not start:
                        break
                    end = f"{start}+{len(word)}c"
                    text_widget.tag_add(f"highlight_{word}", start, end)
                    text_widget.tag_config(f"highlight_{word}", foreground=color)
                    start = end

    def save_file(self):
        tab = self.text_areas[self.tab]
        tab_title = self.notebook.tab(self.tab, option="text")
        if tab_title.startswith("Tab"):
            self.save_file_as()
        else:
            file_path = self.notebook.tab(self.tab, option="text")
            try:
                with open(file_path, "w") as file:
                    content = tab.get("1.0", tk.END)
                    file.write(content)
                messagebox.showinfo("Save", "File saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")

    def save_file_as(self):
        tab = self.text_areas[self.tab]
        file_path = tk.filedialog.asksaveasfilename(defaultextension="*.*", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            try:
                with open(file_path, "w") as file:
                    content = tab.get("1.0", tk.END)
                    file.write(content)
                self.notebook.tab(self.tab, text=file_path)
                messagebox.showinfo("Save As", "File saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")

    def cut(self):
        self.text_areas[self.tab].event_generate("<<Cut>>")

    def copy(self):
        self.text_areas[self.tab].event_generate("<<Copy>>")

    def paste(self):
        self.text_areas[self.tab].event_generate("<<Paste>>")

    def select_all(self):
        self.text_areas[self.tab].tag_add(tk.SEL, "1.0", tk.END)
        self.text_areas[self.tab].mark_set(tk.INSERT, "1.0")
        self.text_areas[self.tab].see(tk.INSERT)

    def info(self):
        version = 7.9
        messagebox.showinfo("Info", f"""
        version {version} 
        IC Text Editor was made by Igor Cielniak.
        © 2023 Igor Cielniak all rights reserved.""")

    def license(self):
        messagebox.showinfo("Licence", """
Copyright 2023 Igor Cielniak

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

        """)

    def add_tab_with_table(self):
        table_sizeh = simpledialog.askinteger("Table Size", "Enter table size horizontal:")
        table_sizev = simpledialog.askinteger("Table Size", "Enter table size vertical:")
        frame = tk.Frame(self.notebook)
        rows = []
        try:
            for i in range(int(table_sizev)):
                cols = []
                for j in range(int(table_sizeh)):
                    e = tk.Entry(frame, relief=tk.GROOVE)
                    e.grid(row=i, column=j, sticky=tk.NSEW)
                rows.append(cols)
            self.notebook.add(frame, text="Table")
        except TypeError:
            return
        messagebox.showinfo("Table", "Table should be in new tab")

    def shortcuts(self):
        root2 = tk.Tk()
        root2.title("Shortcuts")

        tree = ttk.Treeview(root2, columns=('1', '2'), show='headings')
        tree.pack()

        tree.heading('1', text='Function')
        tree.heading('2', text='Keys')

        tree.insert('', '0', values=('New tab', 'Control-Shift-N'))
        tree.insert('', '1', values=('Close tab', 'Control-Shift-C'))
        tree.insert('', '2', values=('Save', 'Control-Shift-S'))
        tree.insert('', '3', values=('Date/time', 'Control-Shift-D'))
        tree.insert('', '5', values=('Find text', 'Control-Shift-F'))
        tree.insert('', '6', values=('Open file', 'Control-Shift-O'))
        tree.insert('', '7', values=('Table', 'Control-Shift-T'))

        root.mainloop()

    def write_date_time(self):
        now = datetime.datetime.now()
        date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
        text_widget = self.text_areas[self.tab]
        cursor_pos = text_widget.index(tk.INSERT)
        text_widget.insert(cursor_pos, date_time_str)

    def auto_complete(self):
        current_text = self.text_areas[self.tab].get("1.0", tk.END).split()
        current_word = current_text[len(current_text) - 1]
        if self.suggestions[0].startswith(current_word):
            text_widget = self.text_areas[self.tab]
            cursor_pos = text_widget.index(tk.INSERT)
            first_suggestion = self.suggestions_listbox.get(0)
            cursor_pos = cursor_pos.split(".")
            line = str(cursor_pos[0])
            cursor_pos = int(cursor_pos[1])
            current_word = int(len(current_word))
            result = line + "." + str(cursor_pos - current_word)
            cursor_pos = line + "." + str(cursor_pos)
            text_widget.delete(result, cursor_pos)
            text_widget.insert(cursor_pos, first_suggestion)
    
    def run(self):
        tab_title = self.notebook.tab(self.tab, option="text")
        if tab_title.startswith("Tab"):
            self.save_file_as()
        else:
            file_path = self.notebook.tab(self.tab, option="text")
            try:
                PryzmaInterpreter.interpret_file(PryzmaInterpreter,file_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to run: {str(e)}")

    def terminalheightfunc(self):
        terminalrelheight = simpledialog.askfloat("Change terminal height", "Enter new height:")
        self.notebookpady = (root.winfo_screenheight() - self.pixeloffset) * terminalrelheight
        self.notebook.pack(expand=tk.YES, fill=tk.BOTH, pady = (0,self.notebookpady))
        if terminalrelheight:
            terminalrely = 1 - terminalrelheight
            terminal.place(relx=0, rely = terminalrely, relwidth=1, relheight=terminalrelheight)







class PryzmaInterpreter:
    
    def __init__(PryzmaInterpreter):
        PryzmaInterpreter.variables = {}
        PryzmaInterpreter.functions = {}

    def interpret_file(PryzmaInterpreter, file_path, *args):
        PryzmaInterpreter.file_path = file_path.strip('"')
        arg_count = 0
        for arguments in args:
            PryzmaInterpreter.variables[f"parg{arg_count}"] = args[arg_count]
            arg_count += 1
        try:
            with open(PryzmaInterpreter.file_path, 'r') as file:
                program = file.read()
                PryzmaInterpreter.interpret(PryzmaInterpreter, program)
        except FileNotFoundError:
            print(f"File '{PryzmaInterpreter.file_path}' not found.")

    def define_function(PryzmaInterpreter, name, body):
        PryzmaInterpreter.functions[name] = body

    def interpret(PryzmaInterpreter, program):
        lines = program.split('\n')
        PryzmaInterpreter.current_line = 0
        
        for line in lines:
            PryzmaInterpreter.current_line += 1
            line = line.strip()

            try:
                if line.startswith("print"):
                    value = line[len("print"):].strip()
                    PryzmaInterpreter.print_value(PryzmaInterpreter, value)
                elif line.startswith("cprint"):
                    value = line[len("cprint"):].strip()
                    PryzmaInterpreter.cprint_value(PryzmaInterpreter, value)
                elif line.startswith("input"):
                    variable = line[len("input"):].strip()
                    PryzmaInterpreter.custom_input(PryzmaInterpreter, variable)
                elif line.startswith("for"):
                    loop_statement = line[len("for"):].strip()
                    loop_var, range_expr, action = loop_statement.split(",", 2)
                    loop_var = loop_var.strip()
                    range_expr = range_expr.strip()
                    action = action.strip()
                    PryzmaInterpreter.for_loop(PryzmaInterpreter, loop_var, range_expr, action)
                elif line.startswith("use"):
                    file_path = line[len("use"):].strip()
                    PryzmaInterpreter.import_functions(PryzmaInterpreter, file_path)
                elif line.startswith("ifs"):
                    condition_actions = line[len("ifs"):].split(",")
                    if len(condition_actions) != 3:
                        print("Invalid if instruction. Expected format: ifs condition, value, action")
                        continue
                    condition = condition_actions[0].strip()
                    value = condition_actions[1].strip()
                    action = condition_actions[2].strip()
                    if condition.startswith('"') and condition.endswith('"'):
                        condition = condition[1:-1]
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    if value in PryzmaInterpreter.variables:
                        value = PryzmaInterpreter.variables[value]
                    if condition in PryzmaInterpreter.variables:
                        condition = PryzmaInterpreter.variables[condition]
                    if condition == "*" or action == "*":
                        PryzmaInterpreter.interpret(PryzmaInterpreter, action)
                    elif value > condition:
                        PryzmaInterpreter.interpret(PryzmaInterpreter, action)
                elif line.startswith("ifb"):
                    condition_actions = line[len("ifb"):].split(",")
                    if len(condition_actions) != 3:
                        print("Invalid if instruction. Expected format: ifb condition, value, action")
                        continue
                    condition = condition_actions[0].strip()
                    value = condition_actions[1].strip()
                    action = condition_actions[2].strip()
                    if condition.startswith('"') and condition.endswith('"'):
                        condition = condition[1:-1]
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    if value in PryzmaInterpreter.variables:
                        value = PryzmaInterpreter.variables[value]
                    if condition in PryzmaInterpreter.variables:
                        condition = PryzmaInterpreter.variables[condition]
                    if condition == "*" or action == "*":
                        PryzmaInterpreter.interpret(PryzmaInterpreter, action)
                    elif value < condition:
                        PryzmaInterpreter.interpret(PryzmaInterpreter, action)
                elif line.startswith("ifn"):
                    condition_actions = line[len("ifn"):].split(",")
                    if len(condition_actions) != 3:
                        print("Invalid if instruction. Expected format: ifn condition, value, action")
                        continue
                    condition = condition_actions[0].strip()
                    value = condition_actions[1].strip()
                    action = condition_actions[2].strip()
                    if condition.startswith('"') and condition.endswith('"'):
                        condition = condition[1:-1]
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    if value in PryzmaInterpreter.variables:
                        value = PryzmaInterpreter.variables[value]
                    if condition in PryzmaInterpreter.variables:
                        condition = PryzmaInterpreter.variables[condition]
                    if condition == "*" or action == "*":
                        PryzmaInterpreter.interpret(PryzmaInterpreter, action)
                    elif value != condition:
                        PryzmaInterpreter.interpret(PryzmaInterpreter, action)
                elif line.startswith("if"):
                    condition_actions = line[len("if"):].split(",")
                    if len(condition_actions) != 3:
                        print("Invalid if instruction. Expected format: if condition, value, action")
                        continue
                    condition = condition_actions[0].strip()
                    value = condition_actions[1].strip()
                    action = condition_actions[2].strip()
                    if condition.startswith('"') and condition.endswith('"'):
                        condition = condition[1:-1]
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    if value in PryzmaInterpreter.variables:
                        value = PryzmaInterpreter.variables[value]
                    if condition in PryzmaInterpreter.variables:
                        condition = PryzmaInterpreter.variables[condition]
                    if condition == "*" or action == "*":
                        PryzmaInterpreter.interpret(PryzmaInterpreter, action)
                    elif value == condition:
                        PryzmaInterpreter.interpret(PryzmaInterpreter, action)
                elif line.startswith("/"):
                    PryzmaInterpreter.variable_definition_in_function_body = "no"
                    function_definition = line[1:].split("{")
                    if len(function_definition) == 2:
                        function_name = function_definition[0].strip()
                        function_body = function_definition[1].strip().rstrip("}")
                        function_body2 = function_body.split("|")
                        PryzmaInterpreter.define_function(PryzmaInterpreter, function_name, function_body2)
                    else:
                        print(f"Invalid function definition: {line}")
                elif line.startswith("@"):
                    function_name = line[1:].strip()
                    if "(" in function_name:
                        function_name, arg = function_name.split("(") 
                        arg = arg.strip(")")
                        if arg:
                            arg = arg.split(",")
                            for args in range(len(arg)):
                                arg[args] = arg[args].lstrip()
                            for args in range(len(arg)):
                                if arg[args].startswith('"') and arg[args].endswith('"'):
                                    PryzmaInterpreter.variables[f'arg{args+1}'] = arg[args][1:-1]
                                elif arg[args] in PryzmaInterpreter.variables:
                                    PryzmaInterpreter.variables[f'arg{args+1}'] = PryzmaInterpreter.variables[arg[args]]
                                elif arg[args].isdigit():
                                    PryzmaInterpreter.variables[f'arg{args+1}'] = int(arg[args])
                                else:
                                    print(f"Invalid argument at line {PryzmaInterpreter.current_line}")
                                    break
                    if function_name in PryzmaInterpreter.functions:
                        command = 0
                        while command < len(PryzmaInterpreter.functions[function_name]):
                            PryzmaInterpreter.interpret(PryzmaInterpreter, PryzmaInterpreter.functions[function_name][command])
                            command += 1
                    else:
                        print(f"Function '{function_name}' is not defined.")
                elif "=" in line:
                    variable, expression = line.split('=')
                    variable = variable.strip()
                    expression = expression.strip()
                    PryzmaInterpreter.assign_variable(PryzmaInterpreter, variable, expression)
                elif line.startswith("copy"):
                    list1, list2 = line[len("copy"):].split(",")
                    list1 = list1.strip()
                    list2 = list2.strip()
                    for element in PryzmaInterpreter.variables[list1]:
                        PryzmaInterpreter.variables[list2].append(element)
                elif line.startswith("append"):
                    list_name, value = line[len("append"):].split(",")
                    list_name = list_name.strip()
                    value = value.strip()
                    PryzmaInterpreter.append_to_list(PryzmaInterpreter, list_name, value)
                elif line.startswith("pop"):
                    list_name, index = line[len("pop"):].split(",")
                    list_name = list_name.strip()
                    index = index.strip()
                    PryzmaInterpreter.pop_from_list(PryzmaInterpreter, list_name, index)
                elif line.startswith("exec"):
                    line = line[5:]
                    os.system(line)
                elif line.startswith("write(") and line.endswith(")"):
                    file_path, content = line[6:-1].split(",")
                    file_path = file_path.strip()
                    content = content.strip()
                    if content.startswith('"') and content.endswith('"'):
                        content = content[1:-1]
                        if file_path.startswith('"') and file_path.endswith('"'):
                            file_path = file_path[1:-1]
                        PryzmaInterpreter.write_to_file(PryzmaInterpreter, content, file_path)
                    elif file_path.startswith('"') and file_path.endswith('"'):
                        file_path = file_path[1:-1]
                        if content.startswith('"') and content.endswith('"'):
                            content = content[1:-1]
                            PryzmaInterpreter.write_to_file(PryzmaInterpreter, content, file_path)
                        PryzmaInterpreter.write_to_file(PryzmaInterpreter, PryzmaInterpreter.variables[content], file_path)
                    elif content in PryzmaInterpreter.variables:
                        PryzmaInterpreter.write_to_file(str(PryzmaInterpreter, PryzmaInterpreter.variables[content]), file_path)
                    else:
                        print(f"Invalid content at line {PryzmaInterpreter.current_line}: {content}")
                elif line.startswith("del(") and line.endswith(")"):
                    variable = line[4:-1]
                    PryzmaInterpreter.variables.pop(variable)
                elif line.startswith("whilen"):
                    condition_action = line[len("whilen"):].split(",", 2)
                    if len(condition_action) != 3:
                        print("Invalid while loop syntax. Expected format: while condition, value, action")
                        continue
                    condition = condition_action[0].strip()
                    value = condition_action[1].strip()
                    action = condition_action[2].strip()
                    if (condition.startswith('"') and condition.endswith('"')) or (value.startswith('"') and value.endswith('"')):
                        while str(PryzmaInterpreter.evaluate_expression(PryzmaInterpreter, condition)) == str(PryzmaInterpreter.evaluate_expression(PryzmaInterpreter, value)):
                            PryzmaInterpreter.interpret(PryzmaInterpreter, action)
                    else:
                        while str(PryzmaInterpreter.variables[condition]) != str(PryzmaInterpreter.variables[value]):
                            PryzmaInterpreter.interpret(PryzmaInterpreter, action)
                elif line.startswith("while"):
                    condition_action = line[len("while"):].split(",", 2)
                    if len(condition_action) != 3:
                        print("Invalid while loop syntax. Expected format: while condition, value, action")
                        continue
                    condition = condition_action[0].strip()
                    value = condition_action[1].strip()
                    action = condition_action[2].strip()
                    if (condition.startswith('"') and condition.endswith('"')) or (value.startswith('"') and value.endswith('"')):
                        while str(PryzmaInterpreter.evaluate_expression(PryzmaInterpreter, condition)) == str(PryzmaInterpreter, PryzmaInterpreter.evaluate_expression(PryzmaInterpreter, value)):
                            PryzmaInterpreter.interpret(PryzmaInterpreter, action)
                    else:
                        while str(PryzmaInterpreter.variables[condition]) == str(PryzmaInterpreter.variables[value]):
                            PryzmaInterpreter.interpret(PryzmaInterpreter, action)
                elif "++" in line:
                    variable = line.replace("++", "").strip()
                    PryzmaInterpreter.increment_variable(PryzmaInterpreter, variable)
                elif "--" in line:
                    variable = line.replace("--", "").strip()
                    PryzmaInterpreter.decrement_variable(PryzmaInterpreter, variable)
                elif line.startswith("move(") and line.endswith(")"):
                    instructions = line[5:-1].split(",")
                    if len(instructions) != 3:
                        print("Invalid move instruction syntax. Expected format: move(old index, new index, list name)")
                        continue
                    list_name = instructions[2].strip()
                    try:
                        old_index = int(instructions[0])
                        new_index = int(instructions[1])
                        value = PryzmaInterpreter.variables[list_name].pop(old_index)
                        PryzmaInterpreter.variables[list_name].insert(new_index, value)
                    except ValueError:
                        print("Invalid index")
                elif line.startswith("swap(") and line.endswith(")"):
                    instructions = line[5:-1].split(",")
                    if len(instructions) != 3:
                        print("Invalid swap instruction syntax. Expected format: swap(index 1, index 2, list name)")
                        continue
                    list_name = instructions[2].strip()
                    index_1 = instructions[0].strip()
                    index_2 = instructions[1].strip()
                    if index_1 in PryzmaInterpreter.variables:
                        index_1 = PryzmaInterpreter.variables[index_1]
                    if index_2 in PryzmaInterpreter.variables:
                        index_2 = PryzmaInterpreter.variables[index_2]
                    try:
                        PryzmaInterpreter.variables[list_name][index_1], PryzmaInterpreter.variables[list_name][index_2] = PryzmaInterpreter.variables[list_name][index_2], PryzmaInterpreter.variables[list_name][index_1]
                    except ValueError:
                        print("Invalid index")
                elif line == "stop":
                    input("Press any key to continue...")
                    break
                else:
                    if line == "" or line.startswith(""):
                        continue
                    else:
                        print(f"Invalid statement at line {PryzmaInterpreter.current_line}: {line}")
            except Exception as e:
                print(f"Error at line {PryzmaInterpreter.current_line}: {e}")

    def decrement_variable(PryzmaInterpreter, variable):
        if variable in PryzmaInterpreter.variables:
            if isinstance(PryzmaInterpreter.variables[variable], int):
                PryzmaInterpreter.variables[variable] -= 1
            else:
                print(f"Error: Cannot decrement non-integer variable '{variable}'.")
        else:
            print(f"Error: Variable '{variable}' not found.")

    def increment_variable(PryzmaInterpreter, variable):
        if variable in PryzmaInterpreter.variables:
            if isinstance(PryzmaInterpreter.variables[variable], int):
                PryzmaInterpreter.variables[variable] += 1
            else:
                print(f"Error: Cannot increment non-integer variable '{variable}'.")
        else:
            print(f"Error: Variable '{variable}' not found.")


    def write_to_file(PryzmaInterpreter, content, file_path):
        try:
            with open(file_path, 'w+') as file:
                if isinstance(content, list):
                    for line in content:
                        file.write(f"{line}\n")
                else:
                    file.write(content)
        except Exception as e:
            print(f"Error writing to file '{file_path}': {e}")

    def assign_variable(PryzmaInterpreter, variable, expression):
        PryzmaInterpreter.variables[variable] = PryzmaInterpreter.evaluate_expression(PryzmaInterpreter, expression)

    def evaluate_expression(PryzmaInterpreter, expression):
        if re.match(r"^\d+$", expression):
            return int(expression)
        elif re.match(r'^".*"$', expression):
            return expression[1:-1]
        elif expression in PryzmaInterpreter.variables:
            return PryzmaInterpreter.variables[expression]
        elif "+" in expression:
            parts = expression.split("+")
            evaluated_parts = [PryzmaInterpreter.evaluate_expression(PryzmaInterpreter, part.strip()) for part in parts]
            if all(isinstance(part, int) for part in evaluated_parts):
                return sum(evaluated_parts)
            elif all(isinstance(part, str) for part in evaluated_parts):
                return "".join(evaluated_parts)
        elif "=" in expression:
            var, val = expression.split("=")
            var = var.strip()
            val = val.strip()
            if var.startswith("int(") and var.endswith(")"):
                if PryzmaInterpreter.var in PryzmaInterpreter.variables:
                    return int(PryzmaInterpreter.variables[var])
                return int(PryzmaInterpreter.evaluate_expression(PryzmaInterpreter, val))
            elif var.startswith("str(") and var.endswith(")"):
                if PryzmaInterpreter.var in PryzmaInterpreter.variables:
                    return str(PryzmaInterpreter.variables[var])
                return str(PryzmaInterpreter.evaluate_expression(PryzmaInterpreter, val))
            else:
                return PryzmaInterpreter.evaluate_expression(PryzmaInterpreter, val)
        elif expression.startswith("type(") and expression.endswith(")"):
            return str(type(PryzmaInterpreter.variables[expression[5:-1]]))
        elif expression.startswith("len(") and expression.endswith(")"):
            return len(PryzmaInterpreter.variables[expression[4:-1]])
        elif expression.startswith("splitby(") and expression.endswith(")"):
            args = expression[8:-1].split(",")
            if len(args) != 2:
                print("Invalid number of arguments for splitby function.")
                return None
            char_to_split = args[0].strip()
            string_to_split = args[1].strip()
            if string_to_split in PryzmaInterpreter.variables:
                string_to_split = PryzmaInterpreter.variables[string_to_split]
            if char_to_split in PryzmaInterpreter.variables:
                char_to_split = PryzmaInterpreter.variables[char_to_split]
            if char_to_split.startswith('"') and char_to_split.endswith('"'):
                char_to_split = char_to_split[1:-1]
            if string_to_split.startswith('"') and string_to_split.endswith('"'):
                string_to_split = string_to_split[1:-1]
            return string_to_split.split(char_to_split)
        elif expression.startswith("split(") and expression.endswith(")"):
            expression = expression[6:-1]
            if expression in PryzmaInterpreter.variables:
                expression = PryzmaInterpreter.variables[expression]
            if expression.startswith('"') and expression.endswith('"'):
                expression = expression[1:-1]
            return expression.split()
        elif expression.startswith("splitlines(") and expression.endswith(")"):
            return PryzmaInterpreter.variables[expression[11:-1]].splitlines()
        elif expression.startswith("read(") and expression.endswith(")"):
            file_path = expression[5:-1]
            if file_path.startswith('"') and file_path.endswith('"'):
                file_path = file_path[1:-1]
            try:
                with open(file_path, 'r') as file:
                    return file.read()
            except FileNotFoundError:
                print(f"File '{file_path}' not found.")
                return ""
        elif expression.startswith("in(") and expression.endswith(")"):
            list_name, value = expression[3:-1].split(",")
            list_name = list_name.strip()
            value = value.strip()
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
                return value in PryzmaInterpreter.variables[list_name]
            elif value.isnumeric():
                return int(value) in PryzmaInterpreter.variables[list_name]
            elif value in PryzmaInterpreter.variables:
                return PryzmaInterpreter.variables[value] in PryzmaInterpreter.variables[list_name]
            else:
                print(f"Variable '{value}' is not defined.")
        elif expression.startswith("index(") and expression.endswith(")"):
            args = expression[6:-1].split(",")
            if len(args) != 2:
                print("Invalid number of arguments for index function.")
                return None
            list_name = args[0].strip()
            value = args[1].strip()
            if list_name in PryzmaInterpreter.variables and isinstance(PryzmaInterpreter.variables[list_name], list):
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                else:
                    if value in PryzmaInterpreter.variables:
                        value = PryzmaInterpreter.variables[value]
                    else:
                        value = int(value)
                try:
                    index_value = PryzmaInterpreter.variables[list_name].index(value)
                    return index_value
                except ValueError:
                    print(f"Value '{value}' not found in list '{list_name}'.")
            else:
                print(f"Variable '{list_name}' is not a list.")
        elif expression.startswith("all(") and expression.endswith(")"):
            list_name = expression[4:-1]
            if list_name in PryzmaInterpreter.variables and isinstance(PryzmaInterpreter.variables[list_name], list):
                return " ".join(map(str, PryzmaInterpreter.variables[list_name]))
            else:
                print(f"List '{list_name}' is not defined.")
                return None
        elif expression.startswith("isanumber(") and expression.endswith(")"):
            expression = expression[10:-1]
            if expression in PryzmaInterpreter.variables:
                expression = PryzmaInterpreter.variables[expression]
                return str(expression).isnumeric()
            else:
                print(f"Variable '{expression}' is not defined.")
                return None
        else:
            try:
                return eval(expression, {}, PryzmaInterpreter.variables)
            except NameError:
                print(f"Unknown variable or expression: {expression}")
        return None

    def print_value(PryzmaInterpreter, value):
        evaluated_value = PryzmaInterpreter.evaluate_expression(PryzmaInterpreter, value)
        if evaluated_value is not None:
            if isinstance(evaluated_value, str) and '\\n' in evaluated_value:
                print(evaluated_value.replace('\\n', '\n'))
            else:
                print(evaluated_value)
            
    def cprint_value(PryzmaInterpreter, value):
        evaluated_value = PryzmaInterpreter.evaluate_expression(PryzmaInterpreter, value)

        if evaluated_value is not None:
            if isinstance(evaluated_value, str) and '\\n' in evaluated_value:
                print(evaluated_value.replace('\\n', '\n'))
            elif re.match(r"^\d+$", str(evaluated_value)):
                print(evaluated_value)
            else:
                print(PryzmaInterpreter.evaluate_expression(PryzmaInterpreter, evaluated_value))

    def custom_input(PryzmaInterpreter, variable):
        if "::" in variable:
            variable_name, prompt = variable.split("::", 1)
            variable_name = variable_name.strip()
            prompt = prompt.strip('"')
        else:
            variable_name = variable.strip()
            prompt = ""

        value = PryzmaInterpreter.get_input(PryzmaInterpreter, prompt)
        PryzmaInterpreter.variables[variable_name] = value

    def for_loop(PryzmaInterpreter, loop_var, range_expr, action):
        start, end = range_expr.split(":")
        start_val = PryzmaInterpreter.evaluate_expression(PryzmaInterpreter, start)
        end_val = PryzmaInterpreter.evaluate_expression(PryzmaInterpreter, end)
        
        if isinstance(start_val, int) and isinstance(end_val, int):
            for val in range(start_val, end_val + 1):
                PryzmaInterpreter.variables[loop_var] = val
                PryzmaInterpreter.interpret(PryzmaInterpreter, action)
        else:
            print("Invalid range expression for loop.")

    def import_functions(PryzmaInterpreter, file_path):
        file_path = file_path.strip('"')
        if file_path.startswith("./"):
            current_directory = os.path.dirname(PryzmaInterpreter.file_path)
            absolute_file_path = os.path.join(current_directory, file_path[2:])
            with open(absolute_file_path, 'r') as file:
                program = file.read()
                lines = program.split('\n')
                function_def = False
                function_name = ""
                function_body = []
                for line in lines:
                    line = line.strip()
                    if line.startswith("/"):
                        if function_def:
                            PryzmaInterpreter.define_function(PryzmaInterpreter, function_name, function_body)
                            function_def = False
                        function_definition = line[1:].split("{")
                        if len(function_definition) == 2:
                            function_name = function_definition[0].strip()
                            function_body = function_definition[1].strip().rstrip("}").split("|")
                            function_def = True
                        else:
                            print(f"Invalid function definition: {line}")
                    elif line.startswith("") or line.startswith(""):
                        continue
                    else:
                        print(f"Invalid statement in imported file: {line}")
                if function_def:
                    PryzmaInterpreter.define_function(PryzmaInterpreter, function_name, function_body)
        else:
            with open(file_path, 'r') as file:
                program = file.read()
                lines = program.split('\n')
                function_def = False
                function_name = ""
                function_body = []
                for line in lines:
                    line = line.strip()
                    if line.startswith("/"):
                        if function_def:
                            PryzmaInterpreter.define_function(PryzmaInterpreter, function_name, function_body)
                            function_def = False
                        function_definition = line[1:].split("{")
                        if len(function_definition) == 2:
                            function_name = function_definition[0].strip()
                            function_body = function_definition[1].strip().rstrip("}").split("|")
                            function_def = True
                        else:
                            print(f"Invalid function definition: {line}")
                    elif line.startswith("") or line.startswith(""):
                        continue
                    else:
                        print(f"Invalid statement in imported file: {line}")
                if function_def:
                    PryzmaInterpreter.define_function(PryzmaInterpreter, function_name, function_body)

    def get_input(PryzmaInterpreter, prompt):
        if sys.stdin.isatty():
            return input(prompt)
        else:
            sys.stdout.write(prompt)
            sys.stdout.flush()
            return sys.stdin.readline().rstrip('\n')

    def evaluate_condition(PryzmaInterpreter, condition):
        if condition in PryzmaInterpreter.variables:
            return bool(PryzmaInterpreter.variables[condition])
        else:
            print(f"Unknown variable in condition: {condition}")
            return False

    def interpret_file2(PryzmaInterpreter):
        PryzmaInterpreter.file_path = input("Enter the file path of the program: ")
        PryzmaInterpreter.interpret_file(PryzmaInterpreter, PryzmaInterpreter.file_path)

    def show_license(PryzmaInterpreter):
        license_text = """
Pryzma
Copyright 2024 Igor Cielniak

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
        """

        print(license_text)
    
    def append_to_list(PryzmaInterpreter, list_name, value):
        if list_name in PryzmaInterpreter.variables:
            PryzmaInterpreter.variables[list_name].append(PryzmaInterpreter.evaluate_expression(PryzmaInterpreter, value))
        else:
            print(f"List '{list_name}' does not exist.")

    def pop_from_list(PryzmaInterpreter, list_name, index):
        if list_name in PryzmaInterpreter.variables:
            try:
                if index.isnumeric():
                    index = int(index)
                else:
                    index = PryzmaInterpreter.variables[index]
                PryzmaInterpreter.variables[list_name].pop(index)
            except IndexError:
                print(f"Index {index} out of range for list '{list_name}'.")
                return
        else:
            print(f"List '{list_name}' does not exist.")
    
    def print_help(PryzmaInterpreter):
        print("""
commands:
        file - run a program from a file
        cls - clear the functions and variables dictionaries
        clst - set clearing functions and variables dictionaries after program execution to true
        clsf - set clearing functions and variables dictionaries after program execution to false
        exit - exit the interpreter
        help - show this help
        license - show the license
""")






PryzmaInterpreter.__init__(PryzmaInterpreter)


root = tk.Tk()

root.state('zoomed') 

text_editor = TextEditor(root)


terminalrelheight = 0.3
terminalrely = 1 - terminalrelheight

terminal = Terminal(root)
terminal.place(relx=0, rely = terminalrely, relwidth=1, relheight = terminalrelheight)


root.mainloop()

