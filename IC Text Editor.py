import tkinter as tk
import os
import sys
from tkinter import *
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import messagebox
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import datetime

class TextEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("IC Text Editor")
        self.master.geometry("650x450")
        self.notebook = ttk.Notebook(self.master)
        self.master.bind('<Control-Shift-N>', lambda event: self.create_tab())
        self.master.bind('<Control-Shift-C>', lambda event: self.close_tab())
        self.master.bind('<Control-Shift-S>', lambda event: self.save_file())
        self.master.bind('<Control-Shift-D>', lambda event: self.write_date_time())
        self.master.bind('<Control-Shift-F>', lambda event: self.find_text())
        self.master.bind('<Control-Shift-O>', lambda event: self.open_file())
        self.master.bind('<Control-Shift-T>', lambda event: self.add_tab_with_table())
        self.text_areas = []
        self.current_tab = 0
        self.app_dir = os.path.dirname(sys.argv[0])
        self.highlight_rules = {}
        self.load_highlight_rules(["C:\\Users\\User\\Desktop\\work\\projects\\IgorCielniak\\IC Text Editor\\pryzma_syntax_highlighting.txt"]) #example path to syntax file
        self.create_tab()
        self.init_menu()

    def find_text(self):
        text_widget = self.text_areas[self.current_tab]
        
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

    def load_highlight_rules(self, file_paths):
        self.highlight_rules = {}
        for file_path in file_paths:
            try:
                with open(file_path, "r") as file:
                    for line in file:
                        word, color = line.strip().split(":")
                        self.highlight_rules[word.strip()] = color.strip()
            except FileNotFoundError:
                messagebox.showwarning("Warning", f"Highlight rules file not found: {file_path}. No custom highlighting will be applied.")
            except ValueError:
                continue
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load highlight rules from {file_path}: {str(e)}")

    def create_tab(self):
        text_area = ScrolledText(self.notebook, wrap=tk.WORD)
        text_area.bind('<KeyRelease>', self.highlight_words)
        self.text_areas.append(text_area)
        self.notebook.add(text_area, text=f"Tab {len(self.text_areas)}")
        self.notebook.pack(expand=tk.YES, fill=tk.BOTH)
        self.notebook.select(self.current_tab)

    def close_tab(self):
        if len(self.text_areas) > 1:
            current_tab = self.notebook.select()
            self.notebook.forget(current_tab)
            self.text_areas.pop(self.current_tab)
            self.current_tab = self.notebook.index(tk.CURRENT)

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
        menu.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menu, tearoff=0)
        edit_menu.add_command(label="Cut", command=self.cut)
        edit_menu.add_command(label="Copy", command=self.copy)
        edit_menu.add_command(label="Paste", command=self.paste)
        edit_menu.add_command(label="Select All", command=self.select_all)
        menu.add_cascade(label="Edit", menu=edit_menu)

        insert_menu = tk.Menu(menu, tearoff=0)
        insert_menu.add_command(label="Table", command=self.add_tab_with_table)
        insert_menu.add_command(label="Date and time", command=self.write_date_time)
        menu.add_cascade(label="Insert", menu=insert_menu)

        settings_menu = tk.Menu(menu, tearoff=0)
        settings_menu.add_command(label="Change font size", command=self.change_font_size)
        settings_menu.add_command(label="Shortcuts", command=self.shortcats)
        menu.add_cascade(label="Settings", menu=settings_menu)

        about_menu = tk.Menu(menu, tearoff=0)
        about_menu.add_command(label="Info", command=self.info)
        about_menu.add_command(label="Licence", command=self.licencja)
        about_menu.add_command(label="Contact", command=self.contact)
        menu.add_cascade(label="About", menu=about_menu)

    def contact(self):
        messagebox.showinfo("Contact", "igorcielniak.contact@gmail.com")

    def change_font_size(self):
        text_widget = self.text_areas[self.current_tab]
        font_size = simpledialog.askinteger("Change font size", "Enter new font size:")
        if font_size:
            font = text_widget['font']
            font_specs = font.split()
            font_family = font_specs[0]
            text_widget.configure(font=(font_family, font_size))

    def new_file(self):
        self.create_tab()

    def open_file(self):
        file_path = filedialog.askopenfilename(defaultextension="*.*", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*"), ("Pryzma",  "*.pryzma"), ("Doc", "*.doc"), ("python file", "*.py"), ("rtf", "*.rtf"), ("docx", "*.docx"), ("odt", "*.odt"), ("css", "*.css"), ("HTML", "*.html"), ("xml", "*.xml"), ("wps", "*.wps"), ("java script", "*.js"), ("JSON", "*.json")])
        if file_path:
            try:
                with open(file_path, "r") as file:
                    content = file.read()
                    self.create_tab()
                    self.text_areas[self.current_tab].delete("1.0", tk.END)
                    self.text_areas[self.current_tab].insert(tk.END, content)
                    self.notebook.tab(self.current_tab, text=os.path.basename(file_path))
                    self.highlight_words(event=None)
                    messagebox.showinfo("Info", f"File opened: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {str(e)}")

    def highlight_words(self, event):
        text_widget = self.text_areas[self.current_tab]
        text_widget.tag_remove("highlight", "1.0", tk.END)
        content = text_widget.get("1.0", tk.END)
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
        current_tab = self.text_areas[self.current_tab]
        tab_title = self.notebook.tab(self.current_tab, option="text")
        if tab_title.startswith("Tab"):
            self.save_file_as()
        else:
            file_path = self.notebook.tab(self.current_tab, option="text")
            try:
                with open(file_path, "w") as file:
                    content = current_tab.get("1.0", tk.END)
                    file.write(content)
                messagebox.showinfo("Save", "File saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")

    def save_file_as(self):
        current_tab = self.text_areas[self.current_tab]
        file_path = filedialog.asksaveasfilename(defaultextension="*.*", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            try:
                with open(file_path, "w") as file:
                    content = current_tab.get("1.0", tk.END)
                    file.write(content)
                self.notebook.tab(self.current_tab, text=file_path)
                messagebox.showinfo("Save As", "File saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")

    def cut(self):
        self.text_areas[self.current_tab].event_generate("<<Cut>>")

    def copy(self):
        self.text_areas[self.current_tab].event_generate("<<Copy>>")

    def paste(self):
        self.text_areas[self.current_tab].event_generate("<<Paste>>")

    def select_all(self):
        self.text_areas[self.current_tab].tag_add(tk.SEL, "1.0", tk.END)
        self.text_areas[self.current_tab].mark_set(tk.INSERT, "1.0")
        self.text_areas[self.current_tab].see(tk.INSERT)

    def info(self):
        version = 7.8
        messagebox.showinfo("Info", f"""
        version {version} 
        IC Text Editor was made by Igor Cielniak.
        © 2023 Igor Cielniak all rights reserved.""")

    def licencja(self):
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
        frame = Frame(self.notebook)
        rows = []
        try:
            for i in range(int(table_sizev)):
                cols = []
                for j in range(int(table_sizeh)):
                    e = Entry(frame, relief=GROOVE)
                    e.grid(row=i, column=j, sticky=NSEW)
                rows.append(cols)
            self.notebook.add(frame, text="Table")
        except TypeError:
            return
        messagebox.showinfo("Table", "Table should be in new tab")

    def shortcats(self):
        root2 = tk.Tk()
        root2.title("Shortcats")

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
        text_widget = self.text_areas[self.current_tab]
        cursor_pos = text_widget.index(tk.INSERT)
        text_widget.insert(cursor_pos, date_time_str)

root = tk.Tk()
text_editor = TextEditor(root)
root.mainloop()
