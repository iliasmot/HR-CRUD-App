import tkinter as tk
from tkinter import ttk
from crud import CRUD

class HREmployeeSearchScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.crud = CRUD(self, self.controller)
        self.currentCRUDAction = None
        self.columns = ["employee.last_name", "employee.first_name", "employee.business_email", "employee.phone",
                        "employee.business_mobile", "employee.personal_mobile", "employee.company_role",
                        "department.dpt_name", "department.building", "department.floor"]
        self.columnDisplayNames = ["Επώνυμο", "Όνομα", "Email", "Εσωτερικό", "Υπηρεσιακό", "Προσωπικό Κινητό",
                                   "Ιδιότητα", "Τμήμα", "Κτήριο", "Όροφος"]

        self.crud.create_header("LogInScreen", "Προσωπικό", "HR 📋") #💼📋
        self.crud.create_search_ui(self.columns, self.columnDisplayNames, self.search)
        self.crud.create_and_pack_export_buttons()
        self.crud.pack_header()
        self.crud.pack_search_ui()

    def search(self, event):
        self.crud.update_search_results(self.search_db(self.crud.searchBar.get()))


    def search_db(self, search_input):
        # connect to database and run query
        database = self.controller.get_database().get_connection()
        cursor = database.cursor()
        if not search_input.strip():  # show everything if input is empty
            query = f"SELECT {', '.join(self.columns)} FROM employee JOIN department ON employee.department_id = department.id"
            cursor.execute(query)
        else:
            query = f"""SELECT {', '.join(self.columns)} FROM employee JOIN department ON employee.department_id = department.id 
	                WHERE employee.first_name LIKE %s OR employee.last_name LIKE %s OR department.dpt_name LIKE %s 
	                    OR employee.company_role LIKE %s;"""
            cursor.execute(query, (f"%{search_input}%", f"%{search_input}%", f"%{search_input}%", f"%{search_input}%",))
        queryResults = cursor.fetchall()
        cursor.close()
        return queryResults

    def update(self):
        self.crud.update_search_results(self.search_db(self.crud.searchBar.get()))
