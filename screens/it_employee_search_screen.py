import tkinter as tk
from tkinter import ttk
from crud import CRUD

class ITEmployeeSearchScreen(tk.Frame):
    """ Screen for searching in the employee database, ment to be used by IT employees."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.crud = CRUD(self, self.controller)
        self.currentCRUDAction = None
        self.columns = ["last_name", "first_name", "email", "phone", "business_mobile", "personal_mobile", "role", "department", "building", "floor"]
        self.columnNames = ["Επώνυμο", "Όνομα", "Email", "Εσωτερικό", "Υπηρεσιακό Κινητό", "Προσωπικό Κινητό", "Ιδιότητα", "Τμήμα", "Κτήριο", "Όροφος"]

        self.crud.create_header("HomeScreen", "Προσωπικό", "IT 🖱") #💻☎️🖥⌨
        self.crud.create_search_ui(self.columns, self.columnNames, self.search)
        self.crud.create_and_pack_export_buttons()
        self.crud.pack_header()
        self.crud.pack_search_ui()


    def search(self, event):
        searchInput = self.crud.searchBar.get()
        database = self.controller.get_database().get_connection()
        cursor = database.cursor()
        query =  """SELECT 
                        employee.last_name, 
                        employee.first_name, 
                        employee.business_email, 
                        employee.phone, 
                        employee.business_mobile,
                        employee.personal_mobile,
                        employee.company_role,  
                        department.dpt_name, 
                        department.building, 
                        department.floor
                    FROM 
                        employee 
                    JOIN 
                        department 
                    ON 
                        employee.department_id = department.id """

        if not searchInput.strip():  # fetch everything if input is empty
            query +=  """WHERE employee.visible = 1;"""
            cursor.execute(query)
        else:
            query += """WHERE 
                        (employee.first_name LIKE %s 
                        OR employee.last_name LIKE %s 
                        OR department.dpt_name LIKE %s)
                        AND employee.visible = 1;"""
            cursor.execute(query, (f"%{searchInput}%", f"%{searchInput}%", f"%{searchInput}%"))

        self.crud.update_search_results(cursor.fetchall())

    def update(self):
        self.search("event")

