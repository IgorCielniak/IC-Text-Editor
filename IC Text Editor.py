import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from tkinter.scrolledtext import ScrolledText
from tkinter.colorchooser import askcolor
import sys
import json
import datetime
import re

try:
    from tkterm import Terminal
except ModuleNotFoundError:
    yn = input("Some modules aren't installed do you want to install them?(y/n)")
    if yn.lower() == "y":
        os.system("pip install tkterm")
        from tkterm import Terminal
    else:
        sys.exit()

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
        self.master.bind('<Control-Shift-L>', lambda event: self.edit_all_occurrences())
        self.text_areas = []
        terminalrelheight = 0.3
        self.pixeloffset = 94
        self.notebookpady = (root.winfo_screenheight() - self.pixeloffset) * terminalrelheight
        self.tab = 0
        self.app_dir = os.path.dirname(sys.argv[0])
        self.highlight_rules = {}
        self.highlighting = tk.IntVar(value=1)
        self.syntax_files = []
        self.load_config(self.app_dir + "\\config.json")
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


    def edit_all_occurrences(self):
        text_widget = self.text_areas[self.tab]
        selected_text = text_widget.get(tk.SEL_FIRST, tk.SEL_LAST) if text_widget.tag_ranges(tk.SEL) else None
        
        if selected_text:
            new_text = simpledialog.askstring("Edit All Occurrences", "Enter new text for all occurrences:", initialvalue=selected_text)
            if new_text is not None:
                replace_method = messagebox.askquestion("Choose Replacement Method",
                                                         "Do you want to replace all occurrences or only exact matches?\n"
                                                         "Click 'Yes' for All, 'No' for Exact Matches.")
                
                content = text_widget.get("1.0", tk.END)
                
                if replace_method == 'yes':
                    updated_content = content.replace(selected_text, new_text)
                else:
                    pattern = r'\b' + re.escape(selected_text) + r'\b'
                    updated_content = re.sub(pattern, new_text, content)
                
                text_widget.delete("1.0", tk.END)
                text_widget.insert("1.0", updated_content)
        else:
            messagebox.showwarning("Warning", "Please select a word to edit all occurrences.")



    
    def open_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.repopulate_tree(folder_path)

    def repopulate_tree(self, path):
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        self.insert_node('', path)

    def insert_node(self, parent, path):
        folder_name = os.path.basename(path)
        full_path = path
        node = self.file_tree.insert(parent, 'end', text=folder_name, open=True, values=(full_path,))

        try:
            for entry in os.listdir(path):
                full_path = os.path.join(path, entry)
                if os.path.isdir(full_path):
                    self.insert_node(node, full_path)
        except Exception as e:
            messagebox.showerror("Error", f"Error accessing directory {path}")


    def on_tree_double_click(self, event):
        item = self.file_tree.selection()[0]
        full_path = self.file_tree.item(item, "values")[0]
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
        self.tree_frame.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, self.notebookpady))
        
        self.file_tree = ttk.Treeview(self.tree_frame)
        self.file_tree.pack(expand=True, fill=tk.BOTH)
        
        self.file_tree.bind("<Double-1>", self.on_tree_double_click)
        
        self.populate_tree()

    def populate_tree(self):
        try:
            path = "."
            self.file_tree.delete(*self.file_tree.get_children())
            abspath = os.path.abspath(path)
            root_node = self.file_tree.insert('', 'end', text=abspath, open=True, values=(abspath,))
            self.process_directory(root_node, abspath)
        except Exception:
            path = self.app_dir
            self.file_tree.delete(*self.file_tree.get_children())
            abspath = os.path.abspath(path)
            root_node = self.file_tree.insert('', 'end', text=abspath, open=True, values=(abspath,))
            self.process_directory(root_node, abspath)

    def process_directory(self, parent, path):
        for p in os.listdir(path):
            abspath = os.path.join(path, p)
            isdir = os.path.isdir(abspath)
            oid = self.file_tree.insert(parent, 'end', text=p, open=False, values=(abspath,))
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
        text_widget = self.text_areas[self.tab]
        file_path = self.notebook.tab(self.tab, option="text")
        if not file_path.startswith("Tab"):
            file_extension = file_path.split(".")[1]
            if file_extension in self.highlight_rules:
                cursor_position = text_widget.index(tk.INSERT)
                word_start = text_widget.search(r'\s', cursor_position, backwards=True, regexp=True)
                word_start = text_widget.index(f"{word_start} +1c")
                current_word2 = self.text_areas[self.tab].get(word_start, cursor_position).splitlines()
                if len(current_word2) != 0:
                    self.current_word = current_word2[0]
                    if current_word2 != "" or type(current_word2) != list:
                        self.suggestions = [word for word in self.highlight_rules[file_extension].keys() if word.startswith(self.current_word)]
                if self.suggestions:
                    self.show_suggestions(self.suggestions)
                else:
                    self.hide_suggestions()


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

    def load_config(self, file_path):
        try:
            with open(file_path, "r") as file:
                config_data = json.load(file)
                if "syntax_files" in config_data:
                    self.syntax_files = config_data["syntax_files"]
                    for syntax_file in self.syntax_files:
                        self.parse_syntax_file(syntax_file)
                if "pryzma_interpreter_path" in config_data:
                    self.pryzma_interpreter_path = config_data["pryzma_interpreter_path"]
                else:
                    self.pryzma_interpreter_path = None
        except FileNotFoundError:
            messagebox.showwarning("Warning", f"Configuration file not found: {file_path}.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration file from {file_path}: {str(e)}")

    def parse_syntax_file(self, syntax_file):
        try:
            with open(syntax_file, "r") as file:
                lines = file.readlines()
                if lines and lines[0].startswith('#'):
                    extension = lines[0][1:].strip()
                    self.highlight_rules[extension] = {}
                    for line in lines[1:]:
                        if ":" in line:
                            word, color = line.strip().split(":")
                            self.highlight_rules[extension][word.strip()] = color.strip()
                else:
                    for line in lines:
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
        file_menu.add_command(label="Open Folder", command=self.open_folder)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.quit)
        menu.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menu, tearoff=0)
        edit_menu.add_command(label="Cut", command=self.cut)
        edit_menu.add_command(label="Copy", command=self.copy)
        edit_menu.add_command(label="Paste", command=self.paste)
        edit_menu.add_command(label="Select All", command=self.select_all)
        edit_menu.add_command(label="Find Text", command=self.find_text)
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
        settings_menu.add_command(label="Refresh File Tree", command=self.refresh_file_tree)
        menu.add_cascade(label="Settings", menu=settings_menu)

        tools_menu = tk.Menu(menu, tearoff=0)
        tools_menu.add_command(label="Run", command=self.run)
        tools_menu.add_command(label="Debug", command=self.debug)
        tools_menu.add_command(label="Interpreter", command=self.interpreter)
        menu.add_cascade(label="Tools", menu=tools_menu)

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
            file_path = self.notebook.tab(self.tab, option="text")
            file_extension = os.path.splitext(file_path)[1][1:]
            if file_extension in self.highlight_rules:
                for word, color in self.highlight_rules[file_extension].items():
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
        tree.insert('', '8', values=('Autocomplete', 'Left Alt'))
        tree.insert('', '9', values=('Replace', 'Control-Shift-L'))

        root.mainloop()

    def write_date_time(self):
        now = datetime.datetime.now()
        date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
        text_widget = self.text_areas[self.tab]
        cursor_pos = text_widget.index(tk.INSERT)
        text_widget.insert(cursor_pos, date_time_str)

    def auto_complete(self):
        text_widget = self.text_areas[self.tab]
        cursor_position = text_widget.index(tk.INSERT)
        word_start = text_widget.search(r'\W', cursor_position, backwards=True, regexp=True)
        word_start = text_widget.index(f"{word_start} +1c")
        if self.suggestions[0].startswith(self.current_word):
            text_widget = self.text_areas[self.tab]
            cursor_pos = text_widget.index(tk.INSERT)
            first_suggestion = self.suggestions_listbox.get(0)
            cursor_pos = cursor_pos.split(".")
            line = str(cursor_pos[0])
            cursor_pos = int(cursor_pos[1])
            len_current_word = int(len(self.current_word))
            result = line + "." + str(cursor_pos - len_current_word)
            cursor_pos = line + "." + str(cursor_pos)
            text_widget.delete(result, cursor_pos)
            text_widget.insert(cursor_pos, first_suggestion)

    def run(self):
        if self.pryzma_interpreter_path != None:
            file_path = self.notebook.tab(self.tab, option="text")
            os.system(str("python " + self.pryzma_interpreter_path + " " + file_path))
            os.system('cls')
        else:
            messagebox.showerror("Error", "Pryzma interpreter path not set. Please set it in settings.")
    
    def debug(self):
        if self.pryzma_interpreter_path != None:
            file_path = self.notebook.tab(self.tab, option="text")
            os.system(str("python " + self.pryzma_interpreter_path + " " + file_path + " " + "--d"))
            os.system('cls')
        else:
            messagebox.showerror("Error", "Pryzma interpreter path not set. Please set it in settings.")
    
    def interpreter(self):
        if self.pryzma_interpreter_path != None:
            os.system(str("python " + self.pryzma_interpreter_path))
            os.system('cls')
        else:
            messagebox.showerror("Error", "Pryzma interpreter path not set. Please set it in settings.")

    def terminalheightfunc(self):
        terminalrelheight = simpledialog.askfloat("Change terminal height", "Enter new height:")
        self.notebookpady = (root.winfo_screenheight() - self.pixeloffset) * terminalrelheight
        self.notebook.pack(expand=tk.YES, fill=tk.BOTH, pady = (0,self.notebookpady))
        self.tree_frame.pack(side=tk.RIGHT, fill=tk.Y, pady=(0,self.notebookpady))
        if terminalrelheight:
            terminalrely = 1 - terminalrelheight
            terminal.place(relx=0, rely = terminalrely, relwidth=1, relheight=terminalrelheight)




root = tk.Tk()

root.state('zoomed')

text_editor = TextEditor(root)


terminalrelheight = 0.3
terminalrely = 1 - terminalrelheight

terminal = Terminal(root)
terminal.place(relx=0, rely = terminalrely, relwidth=1, relheight = terminalrelheight)


root.mainloop()
