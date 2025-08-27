import tkinter as tk
from tkinter import ttk, messagebox
import re


class EmployeeCRUDScreen(tk.Frame):
    """ Screen for searching in the employee database with full CRUD access, ment to be used by an Administrator."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.userType = self.controller.userType
        self.selectedRowValues=[]
        self.currentCRUDAction = ""
        self.searchCriteria = None
        self.resultColumnWidth = 100

        self.create_header(self.controller)
        self.create_search_ui()
        self.create_cud_buttons()
        self.create_cud_menu(self.controller)
        self.place_all_items_in_ui()
        self.show_edit_form(False)

    def create_header(self, controller):
        self.header = ttk.Frame(self)
        self.header.columnconfigure(0, weight=1)
        self.header.columnconfigure(1, weight=1)
        self.header.columnconfigure(2, weight=1)

        self.backButton = ttk.Button(self.header, style="Big.TButton", text="Πίσω",
                                     command=lambda: controller.show_frame("HomeScreen"))
        self.logOutButton = ttk.Button(self.header, style="Big.TButton", text="Αποσύνδεση",
                                       command=lambda: controller.show_frame("LogInScreen"))
        self.screenTitle = ttk.Label(self.header, text="Προσωπικό",
                                     font=(controller.defaultTxtFont, controller.defaultTitleSize))
        self.userIcon = ttk.Label(self.header, text="🦉", font=(self.controller.defaultTxtFont, self.controller.defaultTitleSize, "bold"))

    def create_search_ui(self):
        # search ui
        self.searchBar = ttk.Entry(self, width=50)
        self.searchBar.bind('<KeyRelease>',
                            self.search)  # bind a key release event to the search box to call the function
        self.searchResults = ttk.Treeview(self,
                                          columns=("id", "l_name", "f_name", "email", "b_phone", "b_mobile", "p_mobile",
                                                   "role", "dpt", "building", "floor", "birthday", "name_day", "visible"), show="headings")
        # setting extended result headings
        self.searchResults.heading("id", text="ID",
                                   command=lambda: self.sort_tree(self.searchResults, "f_name", False))
        self.searchResults.heading("f_name", text="Όνομα",
                                   command=lambda: self.sort_tree(self.searchResults, "f_name", False))
        self.searchResults.heading("l_name", text="Επώνυμο",
                                   command=lambda: self.sort_tree(self.searchResults, "l_name", False))
        self.searchResults.heading("email", text="Email",
                                   command=lambda: self.sort_tree(self.searchResults, "email", False))
        self.searchResults.heading("b_phone", text="Εσωτερικός Αριθμός",
                                   command=lambda: self.sort_tree(self.searchResults, "b_phone", False))
        self.searchResults.heading("b_mobile", text="Υπηρεσιακό Κινητό",
                                   command=lambda: self.sort_tree(self.searchResults, "b_mobile", False))
        self.searchResults.heading("p_mobile", text="Προσωπικό Κινητό",
                                   command=lambda: self.sort_tree(self.searchResults, "p_mobile", False))
        self.searchResults.heading("role", text="Ιδιότητα",
                                   command=lambda: self.sort_tree(self.searchResults, "role", False))
        self.searchResults.heading("dpt", text="Τμήμα",
                                   command=lambda: self.sort_tree(self.searchResults, "dpt", False))
        self.searchResults.heading("building", text="Κτήριο",
                                   command=lambda: self.sort_tree(self.searchResults, "building", False))
        self.searchResults.heading("floor", text="Όροφος",
                                   command=lambda: self.sort_tree(self.searchResults, "floor", False))
        self.searchResults.heading("birthday", text="Γενέθλια",
                                   command=lambda: self.sort_tree(self.searchResults, "birthday", False))
        self.searchResults.heading("name_day", text="Γιορτή",
                                   command=lambda: self.sort_tree(self.searchResults, "name_day", False))
        self.searchResults.heading("visible", text="Ορατός",
                                   command=lambda: self.sort_tree(self.searchResults, "visible", False))

        # resizing extended user results
        self.searchResults.column("id", width=50, anchor="center")
        self.searchResults.column("f_name", width=self.resultColumnWidth, anchor="center")
        self.searchResults.column("l_name", width=self.resultColumnWidth, anchor="center")
        self.searchResults.column("email", width=self.resultColumnWidth, anchor="center")
        self.searchResults.column("b_phone", width=self.resultColumnWidth, anchor="center")
        self.searchResults.column("b_mobile", width=self.resultColumnWidth, anchor="center")
        self.searchResults.column("p_mobile", width=100, anchor="center")
        self.searchResults.column("role", width=self.resultColumnWidth, anchor="center")
        self.searchResults.column("dpt", width=self.resultColumnWidth, anchor="center")
        self.searchResults.column("building", width=50, anchor="center")
        self.searchResults.column("floor", width=self.resultColumnWidth, anchor="center")
        self.searchResults.column("birthday", width=50, anchor="center")
        self.searchResults.column("name_day", width=50, anchor="center")
        self.searchResults.column("visible", width=50, anchor="center")

        self.searchResults.bind("<<TreeviewSelect>>", self.get_data_from_selected_row)

    def create_cud_buttons(self):
        # create/update/delete buttons
        self.CUDbuttons = ttk.Frame(self)
        self.CUDbuttons.columnconfigure(0, weight=1)
        self.CUDbuttons.columnconfigure(1, weight=1)
        self.CUDbuttons.columnconfigure(2, weight=1)

        self.createButton = ttk.Button(self.CUDbuttons, style="Big.TButton", text="➕️", command=self.create_employee)
        self.updateButton = ttk.Button(self.CUDbuttons, style="Big.TButton", text="✏", command=self.update_employee)  # 📝🔄 🖌
        self.deleteButton = ttk.Button(self.CUDbuttons, style="Big.TButton", text="❌️", command=self.delete_employee)

    def create_cud_menu(self, controller):
        # initialising frame
        self.cudFrame = ttk.Frame(self)
        self.cudFrame.columnconfigure(0, weight=1)
        self.cudFrame.columnconfigure(1, weight=1)
        self.cudFrame.columnconfigure(2, weight=1)
        self.cudFrame.columnconfigure(3, weight=1)
        self.cudFrame.columnconfigure(4, weight=1)
        self.cudFrame.columnconfigure(5, weight=1)

        # labels for all fields
        self.formTitle = ttk.Label(self.cudFrame, text="Στοιχεία Εργαζομένου", font=(controller.defaultTxtFont, 13))
        self.lnameLabel = ttk.Label(self.cudFrame, text="Επώνυμο: ")
        self.fnameLabel = ttk.Label(self.cudFrame, text="Όνομα: ")
        self.emailLabel = ttk.Label(self.cudFrame, text="Email: ")
        self.phoneLabel = ttk.Label(self.cudFrame, text="Εσωτερικό: ")
        self.bmobileLabel = ttk.Label(self.cudFrame, text="Υπηρεσιακό Κινητό: ")
        self.pmobileLabel = ttk.Label(self.cudFrame, text="Προσωπικό Κινητό: ")
        self.departmentLabel = ttk.Label(self.cudFrame, text="Τμήμα: ")
        self.roleLabel = ttk.Label(self.cudFrame, text="Ιδιότητα: ")
        self.bdayLabel = ttk.Label(self.cudFrame, text="Γενέθλια: ")
        self.ndayLabel = ttk.Label(self.cudFrame, text="Γιορτή: ")

        # input fields (Entries) for all values
        self.lnameEntry = ttk.Entry(self.cudFrame)
        self.fnameEntry = ttk.Entry(self.cudFrame)
        self.emailEntry = ttk.Entry(self.cudFrame)
        self.phoneEntry = ttk.Entry(self.cudFrame)
        self.bmobileEntry = ttk.Entry(self.cudFrame)
        self.pmobileEntry = ttk.Entry(self.cudFrame)
        self.roleEntry = ttk.Entry(self.cudFrame)
        self.bdayEntry = ttk.Entry(self.cudFrame)
        self.ndayEntry = ttk.Entry(self.cudFrame)

        # department dropdown
        self.departmentOptions = self.fetch_departments_from_db()
        self.selectedDepartment = tk.StringVar()
        self.departmentDropdown = ttk.Combobox(self.cudFrame, textvariable=self.selectedDepartment,
                                               values=list(self.departmentOptions.values()),
                                               state="readonly")

        # visibility check box
        self.visibilityVar = tk.IntVar(value=0)
        self.visibleCheckbox = ttk.Checkbutton(self.cudFrame, text="Ορατός", variable=self.visibilityVar)

        # buttons
        self.formClearButton = ttk.Button(self.cudFrame, text="Καθαρισμός", command=self.clear_form_fields)
        self.formsubmitButton = ttk.Button(self.cudFrame, text="Υποβολή", command=self.form_submission)
        self.formCloseButton = ttk.Button(self.cudFrame, text="Ακύρωση", command=self.abort_cud)

        self.formFieldList = (self.lnameEntry, self.fnameEntry, self.emailEntry, self.phoneEntry, self.bmobileEntry,
                              self.pmobileEntry, self.roleEntry, self.departmentDropdown, self.bdayEntry,
                              self.ndayEntry, self.visibilityVar)

    def place_all_items_in_ui(self):
        # displaying UI items
        self.header.pack(fill="x")
        self.backButton.grid(row=0, column=0, sticky="ew", padx="10")
        self.screenTitle.grid(row=0, column=1, padx="350")
        self.logOutButton.grid(row=0, column=2, sticky="ew", padx="10")
        self.userIcon.grid(row=1, column=2, sticky="e", padx=10)
        self.searchBar.pack(pady=10)
        self.searchResults.pack()
        self.CUDbuttons.pack(pady=10)
        self.createButton.grid(row=0, column=0, padx=5)
        self.updateButton.grid(row=0, column=1, padx=5)
        self.deleteButton.grid(row=0, column=2, padx=5)
        # employee info form
        self.cudFrame.pack()
        self.formTitle.grid(row=0, column=0, columnspan=6, pady=5)
        self.fnameLabel.grid(row=1, column=2, pady=5)
        self.fnameEntry.grid(row=1, column=3, pady=5)
        self.lnameLabel.grid(row=1, column=0, pady=5)
        self.lnameEntry.grid(row=1, column=1, pady=5)
        self.emailLabel.grid(row=1, column=4, pady=5)
        self.emailEntry.grid(row=1, column=5, pady=5)
        self.phoneLabel.grid(row=2, column=0, pady=5)
        self.phoneEntry.grid(row=2, column=1, pady=5)
        self.bmobileLabel.grid(row=2, column=2, pady=5 )
        self.bmobileEntry.grid(row=2, column=3, pady=5)
        self.pmobileLabel.grid(row=2, column=4, pady=5)
        self.pmobileEntry.grid(row=2, column=5, pady=5)
        self.roleLabel.grid(row=3, column=0, pady=5)
        self.roleEntry.grid(row=3, column=1, pady=5)
        self.departmentLabel.grid(row=3, column=2, pady=5)
        self.departmentDropdown.grid(row=3, column=3, pady=5)
        self.bdayLabel.grid(row=3, column=4, pady=5)
        self.bdayEntry.grid(row=3, column=5, pady=5)
        self.ndayLabel.grid(row=4, column=0, pady=5)
        self.ndayEntry.grid(row=4, column=1, pady=5)
        self.visibleCheckbox.grid(row=4, column=2, pady=5, padx=5)
        self.formClearButton.grid(row=5, column=0, columnspan=2, sticky="ew", padx=10)
        self.formsubmitButton.grid(row=5, column=2, columnspan=2, sticky="ew", padx=10)
        self.formCloseButton.grid(row=5, column=4, columnspan=2, sticky="ew",padx=10)

    def show_edit_form(self, true):
        " Packs or unpacks the frame that holds the CUD form depanding on the boole given. "
        if true:
            self.cudFrame.pack()
        else:
            self.cudFrame.pack_forget()

    def update(self):
        self.searchBar.focus_set()
        self.update_results("")
        self.show_edit_form(False)

    def search(self, event):
        """ Coordinates all the necessary actions for looking through the database and displaying results when the
        user types anything in the search bar. """
        self.searchCriteria = self.searchBar.get()
        self.update_results(self.searchCriteria)

    def update_results(self, queryCriteria):
        """ Fills the tree view with results from the database"""
        # connect to database
        database = self.controller.get_database().get_connection()
        cursor = database.cursor()

        if not queryCriteria.strip():  # skip if input is empty
            query = """SELECT
                            employee.id, 
                            employee.last_name, 
                            employee.first_name, 
                            employee.business_email, 
                            employee.phone, 
                            employee.business_mobile, 
                            employee.personal_mobile,
                            employee.company_role, 
                            department.dpt_name, 
                            department.building, 
                            department.floor,
                            employee.birthday,
                            employee.name_day,
                            employee.visible
                        FROM employee 
                        JOIN department ON employee.department_id = department.id; """
            cursor.execute(query)
        else:
            query = """SELECT
                            employee.id, 
                            employee.last_name, 
                            employee.first_name, 
                            employee.business_email, 
                            employee.phone, 
                            employee.business_mobile, 
                            employee.personal_mobile,
                            employee.company_role, 
                            department.dpt_name, 
                            department.building, 
                            department.floor,
                            employee.birthday,
                            employee.name_day,
                            employee.visible
                        FROM employee 
                        JOIN department ON employee.department_id = department.id 
                        WHERE 
                            employee.first_name LIKE %s 
                            OR employee.last_name LIKE %s 
                            OR department.dpt_name LIKE %s 
                            OR employee.company_role LIKE %s; 
                        """
            cursor.execute(query, (f"%{queryCriteria}%", f"%{queryCriteria}%", f"%{queryCriteria}%", f"%{queryCriteria}%"))

        queryResults = cursor.fetchall()
        for row in self.searchResults.get_children():
            self.searchResults.delete(row)

        for row in queryResults:
            temp_row = ["" if field is None else field for field in row]  # replace null values with empty strings
            self.searchResults.insert("", tk.END, values=temp_row)
        cursor.close()

    def sort_tree(self, tree, column, reverse):
        """ Sorts the Treeview based on the column clicked. Clicking the column again will cause it to sort rows in reverse. """

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

    def fetch_departments_from_db(self):
        """ Gets all the active departments from the database creating a dictionary with their ID and name. """
        departmentsDict = {}
        database = self.controller.get_database().get_connection()
        cursor = database.cursor()
        query = "SELECT id, dpt_name FROM department"
        cursor.execute(query)
        results = cursor.fetchall()
        departmentsDict = {row[0]: row[1] for row in results}
        return departmentsDict

    def get_dpt_id_from_selection(self):
        """ Gets the selected department from the dropdown menu """
        selectedDptName = self.selectedDepartment.get()
        selectedDptId = next((key for key, value in self.departmentOptions.items() if value == selectedDptName), None)
        return selectedDptId

    def get_data_from_selected_row(self, event):
        selectedRow = self.searchResults.focus()
        self.selectedRowValues = self.searchResults.item(selectedRow, "values")
        if self.currentCRUDAction == "update":
            self.formTitle.configure(text="Ενημέρωση Στοιχείων Εργαζομένου")
            self.populate_form_with_selected_data()

    def populate_form_with_selected_data(self):
        """ Populates the CUD form using the data from self.selectedRowValues. """
        for field in self.formFieldList:
            if field == self.formFieldList[10]: # visibility checkbox
                field.set(0)
            else:
                field.delete(0, tk.END)

        # mapping the pairs of the two indexes (the values from the row and the correpsonding form fields)
        #that is useful because data is skipped like the ID which is not editable by the user, or
        indexMapping = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 11, 9: 12, 10: 13} # form_field : row_value

        for fieldIndex, field in enumerate(self.formFieldList):
            if fieldIndex == 7:
                field.set(self.selectedRowValues[indexMapping[fieldIndex]])
            if fieldIndex == 10:
                field.set(self.selectedRowValues[indexMapping[fieldIndex]])
            else:
                field.insert(0, self.selectedRowValues[indexMapping[fieldIndex]])

    def create_employee(self):
        self.currentCRUDAction = "create"
        self.clear_treeview_selection()
        self.formTitle.configure(text="Καταχώρηση Εργαζομένου")
        self.clear_form_fields()
        self.show_edit_form(True)

    def update_employee(self):
        """ Method that is called when the user clicks the update button """
        if self.selectedRowValues:
            self.currentCRUDAction = "update"
            self.formTitle.configure(text="Ενημέρωση Στοιχείων Εργαζομένου")
            self.show_edit_form(True)
            self.populate_form_with_selected_data()

    def delete_employee(self):
        if self.selectedRowValues:
            response = messagebox.askyesno("ΠΡΟΣΟΧΗ!", "Είστε σίγουροι ότι θέλετε να διαγράψετε τον υπάλληλο;", parent=self)
            if response:
                self.delete_employee_from_db()
                self.clear_form_fields()
                self.cudFrame.pack_forget()

            else:
                pass
        else:
            messagebox.showerror("Σφάλμα", "Παρακαλώ επιλέξτε την εγγραφή που θέλετε να διαγράψετε.")

    def clear_form_fields(self):
        self.fnameEntry.delete(0, tk.END)
        self.lnameEntry.delete(0, tk.END)
        self.emailEntry.delete(0, tk.END)
        self.phoneEntry.delete(0, tk.END)
        self.bmobileEntry.delete(0, tk.END)
        self.pmobileEntry.delete(0, tk.END)
        self.roleEntry.delete(0, tk.END)
        self.bdayEntry.delete(0, tk.END)
        self.ndayEntry.delete(0, tk.END)
        self.departmentDropdown.set("")

    def form_submission(self):
        """ Method that gets executed when the user clicks the submit button in the CRUD form"""
        if self.check_user_input():
            validatedData = self.check_user_input()
            if self.currentCRUDAction == "create": # handling for create user
                self.insert_employee_to_db(validatedData)
                self.clear_form_fields()
            elif self.currentCRUDAction == "update":
                self.update_employee_from_db(validatedData)

    def check_user_input(self):
        """ Checks required fields (department) and acceptable values for phone related fields, email and dates. """
        userInput = self.get_all_form_inputs()
        if not userInput[7]: # Department
            self.show_toast("Το τμήμα είναι υποχρεωτικό.")
            return False
        if not self.validate_email(userInput[2]): # email
            self.show_toast("Το email δεν είναι σωστό.")
            return False

        # check numbers and format them
        if not self.validate_number(userInput[3], True): # phone
            self.show_toast("Το εσωτερικό δεν είναι σωστό")
            return False
        userInput[3] = self.format_phone_number(userInput[3])

        if not self.validate_number(userInput[4], False): # business mobile
            self.show_toast("Το υπηρεσιακό κινητό δεν είναι σωστό")
            return False
        userInput[4] = self.format_phone_number(userInput[4])

        if not self.validate_number(userInput[5], False): # phone
            self.show_toast("Το προσωπικό κινητό δεν είναι σωστό")
            return False
        userInput[5] = self.format_phone_number(userInput[5])

        # check dates
        if not self.validate_date(userInput[8]): # birthday
            self.show_toast("Τα γενέθλια πρέπει να είναι μορφής ηη/μμ.")
            return False

        if not self.validate_date(userInput[9]): # birthday
            self.show_toast("Η γιορτή πρέπει να είναι μορφής ηη/μμ.")
            return False

        return userInput

    def get_all_form_inputs(self):
        formInputList = []
        for index, field in enumerate(self.formFieldList):
            formInputList.insert(index, field.get())
        return formInputList

    def insert_employee_to_db(self, information):
        """ Creates a new employee entry according to the information input by the user """
        if information:
            information[7] = self.get_dpt_id_from_selection()
            query = """INSERT INTO employee 
                        (last_name, first_name, business_email, phone, business_mobile, personal_mobile, company_role, department_id, 
                        birthday, name_day, visible)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
            database = self.controller.get_database().get_connection()
            cursor = database.cursor()
            try:
                cursor.execute(query, information)
                database.commit()
                self.show_toast('Η εγγραφή προστέθηκε επιτυχώς!')
            except Exception as e:
                database.rollback()
                self.show_toast("Η εγγραφή απέτυχε.")
                print(e)

    def update_employee_from_db(self, information):
        """ Updates the selected employee entry according to the information input by the user """
        if information:
            information[7] = self.get_dpt_id_from_selection()
            userID = self.selectedRowValues[0]
            query = """ UPDATE employee 
                        SET last_name = %s, first_name = %s, business_email = %s, phone = %s, 
                            business_mobile = %s, personal_mobile = %s, company_role = %s, department_id = %s, 
                            birthday = %s, name_day = %s, visible = %s
                        WHERE employee.id = """ + str(userID) + ";"
            database = self.controller.get_database().get_connection()
            cursor = database.cursor()
            try:
                cursor.execute(query, information)
                database.commit()
                self.show_toast('Η εγγραφή ενημερώθηκε επιτυχώς!')
                self.update_results(self.searchCriteria)
            except Exception as e:
                database.rollback()
                self.show_toast("Η εγγραφή δεν ενημερώθηκε.")
                print(e)

    def delete_employee_from_db(self):
        userID = self.selectedRowValues[0]
        query = "DELETE FROM employee WHERE employee.id = " + str(userID) + ";"
        database = self.controller.get_database().get_connection()
        cursor = database.cursor()
        try:
            cursor.execute(query)
            database.commit()
            self.show_toast('Η εγγραφή διεγράφη επιτυχώς!')
            self.update_results(self.searchCriteria)
        except Exception as e:
            database.rollback()
            self.show_toast("Η εγγραφή δεν διεγράφη!")
            print(e)

    def clear_treeview_selection(self):
        """ Unselects the selected row in the result treeview. """
        self.searchResults.selection_remove(self.searchResults.selection())
        self.searchResults.focus("")
        self.selectedRowValues = ""

    def show_toast(self, text):
        # main window position
        parent_x = self.winfo_rootx()
        parent_y = self.winfo_rooty()
        parent_width = self.winfo_width()

        # toast size and position
        toast_width = 600
        toast_height = 50
        x = parent_x + (parent_width // 2) - (toast_width // 2)
        y = parent_y + 50

        toast = tk.Toplevel(self)
        toast.overrideredirect(True)  # removes window decorations
        toast.geometry(f"{toast_width}x{toast_height}+{x}+{y}")
        tk.Label(toast, text=text, bg="gray", fg="white", font=("Arial", 20)).pack(
            fill="both", expand=True)
        toast.after(3000, toast.destroy)

    def validate_email(self, email):
        if email:
            pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$" # checking with a regular expression
            return bool(re.match(pattern, email))
        else: # allow for empty fields
            return True

    def validate_number(self, number, is254):
        """ Checks if a phone number contains only digits and the appropriate characters (" " and "/").
        If it's a business landline (is254), it also checks for the appropriate pattern. The method allows for empty
        phone fields. """
        if number:
            if is254 and not ("212254" in number or "212 254" in number): # if it's a business phone check if it follows the known pattern
                return False
            return bool(re.fullmatch(r"[0-9 /]+", number))  # checks if there are only numbers allowing for spaces and slashes
        else: # allow for empty fields
            return True

    def validate_date(self, date):
        pattern = r"^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])$" # regular expression for valid dd/mm
        if date:
            if re.match(pattern, date):
                return True
            else:
                return False
        else:
            return True # allow for empty entry

    def format_phone_number(self, phone):
        if len(phone) == 10 and phone.isdigit():  # ensuring phone number it's exactly 10 digits
            return f"{phone[:3]} {phone[3:6]} {phone[6:]}" # formatting as xxx xxx xxxx
        else: # if there are more phone numbers in the string, don't format
            return phone

    def abort_cud(self):
        self.show_edit_form(False)
        self.currentCRUDAction = ""
        self.clear_form_fields()

