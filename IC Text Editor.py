import tkinter as tk
import os
from tkinter import *
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import messagebox
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import datetime
import webbrowser
import subprocess
from pylab import show, arange, sin, plot, pi
class TextEditor:

    def shourtcats(self):
        root2 = tk.Tk()
        root2.title("Shourtcats")

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

    t = arange(0.0, 2.0, 0.01)
    s = sin( 2 * pi * t)
    plot(t, s)
    
    def Charte(self):

        t = arange(0.0, 2.0, 0.01)
        s = sin( 2 * pi * t)
        plot(t, s)

        show()

    def Chart(self):
        self.Charte()

    def opinion_comments(self):
        webbrowser.open("https://icprogramers-com.webnode.page/kontakt/")

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

    def info(self):
        version = 7.8
        messagebox.showinfo("Info", f"""
        version {version} 
        IC Text Editor was maked by Igor Cielniak.
        © 2023 IC programers all rights reserved.""")


    def licencja(self):
        messagebox.showinfo("Licence", """
Copyright IC programers 2023

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
    
    def prywatność(self):
        messagebox.showinfo("Privacy", """
PRIVACY STATEMENT
1.
The IC Programers company with its registered office in Marki, ul.Piotrówka 14, hereinafter referred to as the "Administrator", cares for the protection of the privacy of its Clients and Users, therefore this Privacy Statement sets out the rules for the processing of personal data that are collected by the Administrator as part of the provision services.
1.
Scope of personal data processing:
The Administrator processes personal data that has been provided voluntarily by Clients or Users when using the services provided by IC Programers. These data may include, among others: name, surname, e-mail address, telephone number, identification data, information about preferences and interests.
2.
Purpose of personal data processing:
Personal data is processed by the Administrator in order to:
providing services in accordance with contracts concluded with customers,
ensuring the safety of using the services provided by IC Programers,
adapting the offer and information provided to Customers and Users to their preferences and interests,
to pursue the Administrator's legitimate interests, such as investigating or defending against claims, auditing, statistics.
3.
Legal basis for the processing of personal data:
The legal basis for the processing of personal data is:
an agreement concluded with the Customer in order to provide services,
the legitimate interests of the Administrator,
consent expressed by the Customer or User to the processing of personal data for a specific purpose.
4.
Recipients of personal data:
Personal data of Clients and Users may be transferred to entities cooperating with IC Programers, such as technical service providers, consultants, auditors, as part of the implementation of services provided by the Administrator.
5.
Personal data storage period:
Personal data will be stored by the Administrator for the period necessary to achieve the purposes for which they were collected, and for the period required by law.
6.
Security of personal data:
The administrator provides appropriate technical and organizational measures to protect personal data against unauthorized access, loss, damage or destruction. These activities include e.g. securing IT infrastructure, monitoring, training employees in the field of privacy protection.
7.
Consent to the processing of personal data:
The processing of personal data is carried out on the basis of the consent expressed by the Client/User or on the basis of another legal basis referred to in point 3 of this Privacy Statement. Consent to the processing of personal data may be withdrawn at any time by the Customer/User, which will not affect the lawfulness of the processing carried out before the withdrawal of consent.
8.
Final Provisions:
This Privacy Statement is an integral part of the agreement concluded between the Client/User and IC Programers regarding the provision of services. The Administrator reserves the right to change this Privacy Statement at any time, which will be communicated to Clients/Users in an appropriate manner. In the event of a change in the provisions of this Privacy Statement, the Customer/User will be able to withdraw consent to the processing of personal data in accordance with the new provisions.
9.
By using the software, you agree to the processing of personal data in accordance with the above subsections.

                            """)



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

    def write_date_time(self):
        now = datetime.datetime.now()
        date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
        
        text_widget = self.text_areas[self.current_tab]

        cursor_pos = text_widget.index(tk.INSERT)
        
        text_widget.insert(cursor_pos, date_time_str)

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
        self.create_tab()
        self.init_menu()

    def create_tab(self):
        text_area = ScrolledText(self.notebook, wrap=tk.WORD)
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
        edit_menu.add_command(label="Find Text", command=self.find_text)
        menu.add_cascade(label="Edit", menu=edit_menu)

        insert_menu = tk.Menu(menu, tearoff=0)
        insert_menu.add_command(label="Table", command=self.add_tab_with_table)
        insert_menu.add_command(label="Chart", command=self.Chart)
        insert_menu.add_command(label="Date and time", command=self.write_date_time)
        menu.add_cascade(label="Insert", menu=insert_menu)

        addons_menu = tk.Menu(menu, tearoff=0)
        addons_menu.add_command(label="add password gen", command=self.add_addon_password)
        addons_menu.add_command(label="Run app", command=self.run)
        menu.add_cascade(label="Addons", menu=addons_menu)

        settings_menu = tk.Menu(menu, tearoff=0)
        settings_menu.add_command(label="Cange font size", command=self.change_font_size)
        settings_menu.add_command(label="Shourtcuts", command=self.shourtcats)
        menu.add_cascade(label="Settings", menu=settings_menu)

        about_menu = tk.Menu(menu, tearoff=0)
        about_menu.add_command(label="Info", command=self.info)
        about_menu.add_command(label="Licence", command=self.licencja)
        about_menu.add_command(label="Privacy", command=self.prywatność)
        about_menu.add_command(label="Website", command=self.strona)
        about_menu.add_command(label="opinion/comments", command=self.opinion_comments)
        menu.add_cascade(label="About", menu=about_menu)

    def change_font_size(self):
        text_widget = self.text_areas[self.current_tab]
        font_size = simpledialog.askinteger("Change font size", "Enter new font size:")
        if font_size:
            font = text_widget['font']
            font_specs = font.split()
            font_family = font_specs[0]
            text_widget.configure(font=(font_family, font_size))

    def quit():
        quit

    def strona(self):
        webbrowser.open("https://icprogramers-com.webnode.page")

    def add_addon_password(self):
        try:
            import ICpasswordgen
            ICpasswordgen.passwordgenerate()
        except ModuleNotFoundError:
            messagebox.showinfo("Addon not found","Addon not found ,you probably change name of file with addon or you don't put it in the same folder as the app.")

    def run(self):

        app_path = simpledialog.askstring("run", """                          Warning:
when path contain spaces it will don't work.
                        Path to app:""")
        process = subprocess.Popen(f"start {app_path}",stdout=subprocess.PIPE, shell=True)
        proc_stdout = process.communicate()[0].strip()
        print(proc_stdout)


    def new_file(self):
        self.create_tab()

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*"), ("Pryzma", "*.pryzma"), ("Doc", "*.doc"), ("python file", "*.py"), ("rtf", "*.rtf"), ("docx", "*.docx"), ("odt", "*.odt"), ("css", "*.css"), ("HTML", "*.html"), ("xml", "*.xml"), ("wps", "*.wps"), ("java script", "*.js"), ("JSON", "*.json")])
        if file_path:
            try:
                with open(file_path, "r") as file:
                    content = file.read()
                    self.create_tab()
                    self.text_areas[self.current_tab].delete("1.0", tk.END)
                    self.text_areas[self.current_tab].insert(tk.END, content)
                    self.notebook.tab(self.current_tab, text=os.path.basename(file_path))
                    messagebox.showinfo("Info", f"File opened: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {str(e)}")

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
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",filetypes=[("Text Files", "*.txt"), ("All Files", "*.*"), ("Pryzma", "*.pryzma"), ("Doc", "*.doc"), ("python file", "*.py"), ("rtf", "*.rtf"), ("docx", "*.docx"), ("odt", "*.odt"), ("css", "*.css"), ("HTML", "*.html"), ("xml", "*.xml"), ("wps", "*.wps"), ("java script", "*.js"), ("JSON", "*.json")])
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


root = tk.Tk()
text_editor = TextEditor(root)
root.mainloop()

#you really went through all the code!?















