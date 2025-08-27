import tkinter as tk
from tkinter import messagebox

from crud import CRUD

class SupplierCRUDScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.crud = CRUD(self, self.controller)
        self.userType = self.controller.userType
        self.selectedRowValues = []
        self.currentCRUDAction = ""
        self.searchCriteria = None
        self.updateTitleForForm = "Ενημέρωση Στοιχείων Προμηθευτή"
        self.resultColumnWidth = 100
        self.columns = ("id", "company_name", "business_type", "associate_last_name", "associate_first_name", "phone",
                        "mobile", "email", "address")
        self.columnDisplayNames = ("ID", "Εταιρεία", "Είδος", "Επώνυμο Συνεργάτη", "Όνομα Συνεργάτη", "Τηλέφωνο", "Κινητό",
                                "Email", "Διεύθυνση")

        self.crud.create_header("HomeScreen", "Προμηθευτές I.T.", "IT 🖱")
        self.crud.create_search_ui(self.columns, self.columnDisplayNames, self.search)
        self.crud.create_and_pack_export_buttons()

        self.crud.pack_header()
        self.crud.pack_search_ui()

        self.crud.create_cud_buttons(self.create_method, self.update_method, self.delete_method)
        self.crud.pack_cud_buttons()
        self.crud.create_cud_form(self.columns, self.columnDisplayNames, "Επεξεργασία Στοιχείων", self.submit_form)
        # self.crud.pack_cud_form()

    def search(self, event):
        self.crud.update_search_results(self.search_db(self.crud.searchBar.get()))

    def search_db(self, search_input):
        # connect to database and run query
        database = self.controller.get_database().get_connection()
        cursor = database.cursor()

        if not search_input.strip():  # return everything if input is empty
            query = f"SELECT {', '.join(self.columns)} FROM supplier"
            cursor.execute(query)
        else:
            query = f"SELECT {', '.join(self.columns)} FROM supplier WHERE company_name LIKE %s OR business_type LIKE %s OR associate_last_name LIKE %s;"
            cursor.execute(query, (f"%{search_input}%", f"%{search_input}%", f"%{search_input}%",))
        results = cursor.fetchall()
        cursor.close()
        return results

    def update_method(self):
        self.currentCRUDAction = "update"
        if (self.crud.selectedRowValues):
            self.crud.populate_form_with_selected_row_data(self.crud.selectedRowValues)
            self.crud.formTitle.configure(text=self.updateTitleForForm)
            self.crud.pack_cud_form()

    def delete_method(self):
        if self.crud.selectedRowValues:
            response = messagebox.askyesno("ΠΡΟΣΟΧΗ!", "Είστε σίγουροι ότι θέλετε να διαγράψετε τον προμηθευτή;", parent=self)
            if response:
                userID = self.crud.selectedRowValues[0]
                query = "DELETE FROM supplier WHERE supplier.id = " + str(userID) + ";"
                database = self.controller.get_database().get_connection()
                cursor = database.cursor()
                try:
                    cursor.execute(query)
                    database.commit()
                    self.crud.show_toast('Η εγγραφή διεγράφη επιτυχώς!')
                    self.crud.update_search_results(self.searchCriteria)
                except Exception as e:
                    database.rollback()
                    self.crud.show_toast("Η εγγραφή δεν διεγράφη!")
                    print(e)
        else:
            messagebox.showerror("Σφάλμα", "Παρακαλώ επιλέξτε την εγγραφή που θέλετε να διαγράψετε.")

    def create_method(self):
        self.currentCRUDAction = "create"
        self.crud.clear_treeview_selection()
        self.crud.clear_form_fields()
        self.crud.formTitle.configure(text="Καταχώρηση Καινούριου Προμηθευτή")
        self.crud.pack_cud_form()

    def submit_form(self):
        if self.validate_user_input():
            validatedData = self.validate_user_input()
            if self.currentCRUDAction == "update":
                self.update_entry_in_db(validatedData)
                self.crud.clear_treeview_selection()
            elif self.currentCRUDAction == "create":
                self.create_entry_in_db(validatedData)
            self.crud.clear_form_fields()
            self.crud.update_search_results(self.search_db(self.crud.searchBar.get()))


    def validate_user_input(self):
        input = self.crud.get_all_form_input()
        if not self.crud.validate_email(self.crud.entries["email"].get()):
            self.crud.show_toast("Το email δεν είναι σωστό.")
            return False

        if not self.crud.validate_number(self.crud.entries["phone"].get()):
            self.crud.show_toast("Το τηλέφωνο δεν είναι σωστό.")
            return False
        input[4] = self.crud.format_phone_number(self.crud.entries["phone"].get())

        if not self.crud.validate_number(self.crud.entries["mobile"].get()):
            self.crud.show_toast("Το κινητό δεν είναι σωστό.")
            return False
        input[5] = self.crud.format_phone_number(self.crud.entries["mobile"].get())

        return input


    def create_entry_in_db(self, data):
        if data:
            query = """INSERT INTO supplier 
                                    (company_name, business_type, associate_last_name, associate_first_name, phone,
                                    mobile, email, address)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"""
            database = self.controller.get_database().get_connection()
            cursor = database.cursor()
            try:
                cursor.execute(query, data)
                database.commit()
                self.crud.show_toast('Η εγγραφή προστέθηκε επιτυχώς!')
            except Exception as e:
                database.rollback()
                self.crud.show_toast("Η εγγραφή απέτυχε.")
                print(e)

    def update_entry_in_db(self, data):
        """ Updates the selected supplier entry according to the information input by the user """
        if data and self.crud.selectedRowValues:
            supplierID = self.crud.selectedRowValues[0]
            query = """ UPDATE supplier 
                                SET company_name = %s, business_type = %s, associate_last_name = %s, associate_first_name = %s, phone = %s, 
                                    mobile = %s, email = %s, address = %s
                                WHERE supplier.id = """ + str(supplierID) + ";"
            database = self.controller.get_database().get_connection()
            cursor = database.cursor()
            try:
                cursor.execute(query, data)
                database.commit()
                self.crud.show_toast('Η εγγραφή ενημερώθηκε επιτυχώς!')
            except Exception as e:
                database.rollback()
                self.crud.show_toast("Η εγγραφή δεν ενημερώθηκε.")
                print(e)

    def update(self):
        self.crud.update_search_results(self.search_db(self.crud.searchBar.get()))
        self.crud.cudFrame.pack_forget()