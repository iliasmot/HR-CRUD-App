import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
import pandas

class CRUD:
    """ Class that contains a variety of methods for easily creating a CRUD UI. Some methods have to be implemented on
    the actual class that the interface is being implemented."""

    def __init__(self, implementationScreen, controller):
        self.implementationScreen = implementationScreen
        self.controller = controller
        self.entryFields = ""
        self.selectedRowValues = ""
        self.email_column_index = -1


    # create elements
    def create_header(self, previous_screen, header_title, user_icon):
        """ Creates a header for the current screen. Accepts the previous screen's name (for navigation) and the desired
        title for the current screen. """
        self.header = ttk.Frame(self.implementationScreen)
        self.header.columnconfigure(0, weight=1)
        self.header.columnconfigure(1, weight=1)
        self.header.columnconfigure(2, weight=1)
        self.userIcon = ttk.Label(self.header, text=user_icon, justify="center", font=(self.controller.defaultTxtFont, self.controller.defaultTitleSize, 'bold'))

        self.backButton = ttk.Button(self.header, style="Big.TButton", text="Πίσω",
                                     command=lambda: self.implementationScreen.controller.show_frame(previous_screen))
        self.logOutButton = ttk.Button(self.header, style="Big.TButton", text="Αποσύνδεση",
                                       command=lambda: self.implementationScreen.controller.show_frame("LogInScreen"))
        self.screenTitle = ttk.Label(self.header, text=header_title,
                                     font=(self.implementationScreen.controller.defaultTxtFont,
                                           self.implementationScreen.controller.defaultTitleSize))

    def create_search_ui(self, columns, column_display_names, search_function):
        """ Method to create a search interface. Accepts a list of names for each result column, a list for the columns'
        display names and the function used to search through the database"""
        # search ui
        self.searchBar = ttk.Entry(self.implementationScreen, width=50)
        self.searchBar.bind('<KeyRelease>', search_function)  # bind a key release event to the search box to call the function
        self.searchResults = ttk.Treeview(self.implementationScreen, columns=(columns), show="headings")

        # setting headers and header sorting
        for index, column in enumerate(columns):
            self.searchResults.heading(column, text=column_display_names[index],
                                       command=lambda f=column: self.sort_tree(self.searchResults, f, False))
            if "mail" in column_display_names[index]:
                self.email_column_index = index
        # resizing user results
        for column in columns:
            if "id" in column:
                self.searchResults.column(column, width=1, anchor="center")
            elif "description" in column:
                self.searchResults.column(column, width=200, anchor="center")
            else:
                self.searchResults.column(column, width=20, anchor="center")

        self.searchResults.bind("<<TreeviewSelect>>", self.get_data_from_selected_row)
        self.searchResults.bind("<Button-3>", self.show_context_menu) #binding for right click

        self.rightClickMenu = tk.Menu(self.implementationScreen, tearoff=0)
        self.rightClickMenu.add_command(label="Copy", command=self.copy_cell_data_to_clipboard)


    def create_and_pack_export_buttons(self):
        """creates and packs two buttons. One for exporting to Excel and one to copy every email address from the fetched search results."""
        self.exportButtonFrame = ttk.Frame(self.implementationScreen)
        self.exportButtonFrame.pack(side="bottom", fill="x", pady=10, padx=10)
        self.exportButtonFrame.columnconfigure(0, weight=1)

        # 📄📃📜📑📊🗃🔠 ➡📊 possible icons
        self.exportButton = ttk.Button(self.exportButtonFrame, text="Εξαγωγή σε Excel", style="Big.TButton", command=self.export_table_to_excel)
        self.exportButton.grid(row=0, column=1, sticky="e")

        self.copySelectedEmailsButton = ttk.Button(self.exportButtonFrame, text="Αντιγραφή e-mail", style="Big.TButton", command=self.copy_fetched_emails_to_clipboard)
        self.copySelectedEmailsButton.grid(row=0, column=0, sticky="w")

    def create_cud_buttons(self, create_method, update_method, delete_method):
        """ Creates three buttons for Create Update and Delete. Accepts three methods as arguments, one for each action,
        which have to be implemented on the implementation class. """
        # create/update/delete buttons
        self.CUDbuttons = ttk.Frame(self.implementationScreen)
        self.CUDbuttons.columnconfigure(0, weight=1)
        self.CUDbuttons.columnconfigure(1, weight=1)
        self.CUDbuttons.columnconfigure(2, weight=1)

        self.createButton = ttk.Button(self.CUDbuttons, style="Big.TButton", text="➕️", command=create_method)
        self.updateButton = ttk.Button(self.CUDbuttons, style="Big.TButton", text="✏",
                                       command=update_method)  # 📝🔄 🖌
        self.deleteButton = ttk.Button(self.CUDbuttons, style="Big.TButton", text="❌️", command=delete_method)

    def create_cud_form(self, entry_fields, entry_field_display_names, form_title, submit_method):
        """ Creates a form that allows the user to input data for creating and updating entries in the database.
        It accepts a list of attributes and a list for the attribute's screen names, a title for the form and the method
        that gets called when the "submit" button is clicked.
        Important:
            -the method skips the first attribute in the lists. That's ment for the entries' ID which in this
                system is not editable by the users and is set to auto-increment.
            -The submit method has to be implemented in the implementation class."""

        # initialising frame
        self.cudFrame = ttk.Frame(self.implementationScreen)
        self.entryFields = entry_fields

        for i in range(6):
            self.cudFrame.columnconfigure(i, weight=1)

        self.labels = {}
        self.entries = {}

        self.formTitle = ttk.Label(self.cudFrame, text=form_title,
                                   font=(self.implementationScreen.controller.defaultTxtFont, 13, "bold"))
        self.formTitle.grid(row=0, column=0, columnspan=6, pady=10)

        # dictionaries for labels and inputs
        self.labels = {}
        self.entries = {}

        row = 1
        col = 0
        for index, field in enumerate(entry_fields):
            if index == 0:
                continue
            self.labels[field] = ttk.Label(self.cudFrame, text=entry_field_display_names[index])
            self.entries[field] = ttk.Entry(self.cudFrame)
            self.labels[field].grid(row=row, column=col, padx=5, pady=5)
            col += 1
            if col == 6:
                col = 0
                row += 1
            self.entries[field].grid(row=row, column=col, padx=5, pady=5)
            col += 1
            if col == 6:
                col = 0
                row += 1

        # buttons
        self.formClearButton = ttk.Button(self.cudFrame, text="Καθαρισμός", command=self.clear_form_fields)
        self.formSubmitButton = ttk.Button(self.cudFrame, text="Υποβολή", command=submit_method)
        self.formCloseButton = ttk.Button(self.cudFrame, text="Ακύρωση", command=self.abort_cud)

        self.formClearButton.grid(row=row+1, column=0, columnspan=2, sticky="ew", padx=10)
        self.formSubmitButton.grid(row=row + 1, column=2, columnspan=2, sticky="ew", padx=10)
        self.formCloseButton.grid(row=row + 1, column=4, columnspan=2, sticky="ew", padx=10)


    # packing
    def pack_header(self):
        """ Packs the header created with create_header(). """
        self.header.pack(fill="x")
        self.backButton.grid(row=0, column=0, sticky="w", padx="10")
        self.screenTitle.grid(row=0, column=1, padx="300")
        self.logOutButton.grid(row=0, column=2, sticky="e", padx="10")
        self.userIcon.grid(row=1, column=2, sticky="e", padx="10")

    def pack_search_ui(self):
        """ Packs the search bar and the TreeView for displaying search results created with create_search_ui(). """
        self.searchBar.pack(pady=10)
        self.searchResults.pack(fill="x", padx=50)

    def pack_cud_buttons(self):
        """ Packs the Create, Update and Delete buttons created with create_cud_buttons().
         to think about later:
            An easy way to limit database edit access would be to simply hide, unpack (pack_forgtet) or not pack these buttons. """
        self.CUDbuttons.pack(pady=10)
        self.createButton.grid(row=0, column=0, padx=5)
        self.updateButton.grid(row=0, column=1, padx=5)
        self.deleteButton.grid(row=0, column=2, padx=5)

    def pack_cud_form(self):
        self.cudFrame.pack()

    def unpack_cud_form(self):
        self.cudFrame.pack_forget()

    def abort_cud(self):
        self.unpack_cud_form()
        self.implementationScreen.currentCRUDAction = ""
        self.clear_form_fields()

    # other
    def update_search_results(self, returned_data):
        """printing results to the TreeView UI"""
        for row in self.searchResults.get_children():  # get rid of old data
            self.searchResults.delete(row)
        for row in returned_data:  # input the new data
            temp_row = ["" if field is None else field for field in row]  # replace null values with empty strings
            self.searchResults.insert("", tk.END, values=temp_row)

    def get_data_from_selected_row(self, event):
        """ Returns the values of the selected row from the result Treeview. """
        if self.implementationScreen.currentCRUDAction:
            selectedRow = self.searchResults.focus()
            self.selectedRowValues = self.searchResults.item(selectedRow, "values")
            if self.implementationScreen.currentCRUDAction == "update":
                self.formTitle.configure(text=self.implementationScreen.updateTitleForForm)
                self.populate_form_with_selected_row_data(self.selectedRowValues)
            # return self.searchResults.item(selectedRow, "values")

    def sort_tree(self, tree, column, reverse):
        """ Sorts the Treeview based on the column clicked. If clicked again it performs a reverse sorting. """

        # getting the data from the specified column
        data = [(tree.set(item, column), item) for item in tree.get_children("")]

        try: #if the data are numbers, try converting them to ints before sorting them
            data.sort(key=lambda x: int(x[0]), reverse=reverse)
        except ValueError: #if that doesn't work, just sort the data
            data.sort(reverse=reverse)

        # rearranging the tree data based on the sorting
        for index, (value, item) in enumerate(data):
            tree.move(item, "", index)

        # switching the reverse argument in the heading set up so that it behaves differently with each click
        tree.heading(column, command=lambda: self.sort_tree(tree, column, not reverse))

    def show_context_menu(self, event):
        """ Display the context menu when right-clicking on a cell. """
        item = self.searchResults.identify_row(event.y)  # Get clicked row
        column = self.searchResults.identify_column(event.x)  # Get clicked column
        if item and column:
            self.selected_item = item
            self.selected_column = column
            self.rightClickMenu.post(event.x_root, event.y_root)  # Show menu at mouse position

    def copy_cell_data_to_clipboard(self):
        """ Copy the selected cell data to the clipboard. """
        column_index = int(self.selected_column[1:]) - 1  # Convert column format (#1, #2...) to index
        cell_value = self.searchResults.item(self.selected_item, "values")[column_index]  # Get cell value

        self.implementationScreen.clipboard_clear()
        self.implementationScreen.clipboard_append(cell_value)
        self.implementationScreen.update()  # Keeps clipboard available even after closing the app

    def copy_fetched_emails_to_clipboard(self):
        """ Gets all email addresses from the fetched results, concatenates them with ";" symbol for outlook
        compatibility and sends them to the clipboard. """
        if self.email_column_index != -1:
            columnData = ""
            for item in self.searchResults.get_children():
                values = self.searchResults.item(item, "values")  # get each row
                if values and values[self.email_column_index]:
                    columnData += values[self.email_column_index] + "; "  # add it to the string
            self.implementationScreen.clipboard_clear()
            self.implementationScreen.clipboard_append(columnData)
            self.implementationScreen.update()  # keeps the clipboard updated

    def clear_form_fields(self):
        """ Clears all the input fields from the CUD "form". """
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def populate_form_with_selected_row_data(self, data):
        """ Populates the CUD "form" with data from the currently selected row in the result TreeView. """
        self.clear_form_fields()
        for index, field in enumerate(self.entries.values()):
            if index+1 < len(data):
                field.insert(0, data[index+1])

    def get_all_form_input(self):
        " Returns all input from the crud form in a list "
        formInputList = []
        for index, field in enumerate(self.entries.values()):
            formInputList.insert(index, field.get())
        return formInputList

    def clear_treeview_selection(self):
        """ Unselects the selected row in the result treeview. """
        self.searchResults.selection_remove(self.searchResults.selection())
        self.searchResults.focus("")
        self.selectedRowValues = ""

        # validation

    def validate_email(self, email):
        """ Checks for a valid e-mail. It accepts the email address as a string and checks it against a regular
        expression. Returns a boolean value according to the outcome. Also returns 'true' if the string is empty,
        allowing for no value."""
        if email:
            pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$" # checking with a regular expression
            return bool(re.match(pattern, email))
        else: # allow for empty fields
            return True

    def validate_number(self, number):
        """ Checks if a phone number contains only digits and the appropriate characters (" " and "/").
        The method allows for empty phone fields. """
        if number:
            return bool(re.fullmatch(r"[0-9 /]+", number))  # checks if there are only numbers allowing for spaces and slashes
        else: # allow for empty fields
            return True

    def validate_date(self, date):
        """ Checks if a given string for a date follows the proper pattern (dd/mm) that we have adopted for our database. """
        pattern = r"^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])$" # regular expression for valid dd/mm
        if date:
            if re.match(pattern, date):
                return True
            else:
                return False
        else:
            return True # allow for empty entry

    def format_phone_number(self, phone):
        """ Formats the phone numbers (string) as XXX XXX XXXX """
        if len(phone) == 10 and phone.isdigit():  # ensuring phone number it's exactly 10 digits
            return f"{phone[:3]} {phone[3:6]} {phone[6:]}" # formatting as xxx xxx xxxx
        else: # if there are more phone numbers in the string, don't format
            return phone

    def export_table_to_excel(self):
        """ Exports all the data from the currently fetched results and exports them to an Excel file. """
        treeview = self.searchResults
        columns = [treeview.heading(col)["text"] for col in treeview["columns"]] # getting column names
        data = []
        for item in treeview.get_children(): # getting all the data
            values = treeview.item(item)["values"]
            data.append(values)

        # creating a DataFrame
        df = pandas.DataFrame(data, columns=columns)

        # prompt to ask user where and with what name to save the file
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])

        if file_path:
            # export to excel
            try:
                df.to_excel(file_path, index=False, engine="openpyxl")
                messagebox.showinfo("Επιτυχία", "Τα δεδομένα εξήχθησαν επιτυχώς στο Excel!")
            except Exception as e:
                messagebox.showerror("Σφάλμα", f"Σφάλμα κατά την εξαγωγή: {e}")

    def show_toast(self, text):
        """ Creates and displays a Toast-like message."""
        # main window position
        parent_x = self.implementationScreen.winfo_rootx()
        parent_y = self.implementationScreen.winfo_rooty()
        parent_width = self.implementationScreen.winfo_width()

        # toast size and position
        toast_width = 600
        toast_height = 50
        x = parent_x + (parent_width // 2) - (toast_width // 2)
        y = parent_y + 50

        toast = tk.Toplevel(self.implementationScreen)
        toast.overrideredirect(True)  # removes window decorations
        toast.geometry(f"{toast_width}x{toast_height}+{x}+{y}")
        tk.Label(toast, text=text, bg="gray", fg="white", font=("Arial", 20)).pack(
            fill="both", expand=True)
        toast.after(3000, toast.destroy)