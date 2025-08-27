import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from crud import CRUD
import pandas


class AssociateCRUDScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.crud = CRUD(self, self.controller)
        self.currentCRUDAction = ""
        self.updateTitleForForm = "Ενημέρωση Στοιχείων Συνεργάτη"

        self.columns = ["id", "last_name", "first_name", "phone", "mobile", "email", "description"]
        self.column_names = ["ID", "Επώνυμο", "Όνομα", "Τηλέφωνο", "Κινητό", "Email", "Περιγραφή"]

        self.crud.create_header("HomeScreen", "Συνεργάτες I.T.", "IT 🖱")
        self.crud.create_search_ui(self.columns, self.column_names, self.search)
        self.crud.create_and_pack_export_buttons()
        self.crud.create_cud_buttons(self.create_associate, self.update_associate, self.delete_associate)
        self.crud.create_cud_form(self.columns, self.column_names, "Επεξεργασία Συνεργατών", self.submit)

        self.crud.pack_header()
        self.crud.pack_search_ui()
        self.crud.pack_cud_buttons()


    def search(self, event):
        self.crud.update_search_results(self.search_db(self.crud.searchBar.get()))

    def search_db(self, search_input):
        # connect to database and run query
        database = self.controller.get_database().get_connection()
        cursor = database.cursor()
        if not search_input.strip():  # show everything if input is empty
            query = f"SELECT {', '.join(self.columns)} FROM associate;"
            cursor.execute(query)
        else:
            query = f"SELECT {', '.join(self.columns)} FROM associate WHERE first_name LIKE %s OR last_name LIKE %s OR description LIKE %s;"
            cursor.execute(query, (f"%{search_input}%", f"%{search_input}%", f"%{search_input}%",))
        queryResults = cursor.fetchall()
        cursor.close()
        return queryResults

    def submit(self):
        if self.validate_user_input():
            validatedData = self.validate_user_input()
            if self.currentCRUDAction == "update":
                self.update_entry_in_db(validatedData)
                self.crud.clear_treeview_selection()
            elif self.currentCRUDAction == "create":
                self.create_entry_in_db(validatedData)
            self.crud.clear_form_fields()
            self.crud.update_search_results(self.search_db(self.crud.searchBar.get()))

    def create_associate(self):
        self.currentCRUDAction = "create"
        self.crud.clear_treeview_selection()
        self.crud.clear_form_fields()
        self.crud.formTitle.configure(text="Καταχώρηση Καινούριου Συνεργάτη")
        self.crud.pack_cud_form()

    def update_associate(self):
        self.currentCRUDAction = "update"
        if (self.crud.selectedRowValues):
            self.crud.populate_form_with_selected_row_data(self.crud.selectedRowValues)
            self.crud.formTitle.configure(text=self.updateTitleForForm)
            self.crud.pack_cud_form()

    def delete_associate(self):
        self.crud.abort_cud()
        if self.crud.selectedRowValues:
            response = messagebox.askyesno("ΠΡΟΣΟΧΗ!", "Είστε σίγουροι ότι θέλετε να διαγράψετε τον συνεργάτη;",
                                           parent=self)
            if response:
                associateID = self.crud.selectedRowValues[0]
                query = "DELETE FROM associate WHERE associate.id = " + str(associateID) + ";"
                database = self.controller.get_database().get_connection()
                cursor = database.cursor()
                try:
                    cursor.execute(query)
                    database.commit()
                    self.crud.show_toast('Η εγγραφή διεγράφη επιτυχώς!')
                    self.crud.update_search_results(self.search_db(self.crud.searchBar.get()))
                except Exception as e:
                    database.rollback()
                    self.crud.show_toast("Η εγγραφή δεν διεγράφη!")
                    print(e)
        else:
            messagebox.showerror("Σφάλμα", "Παρακαλώ επιλέξτε την εγγραφή που θέλετε να διαγράψετε.")

    def validate_user_input(self):
        input = self.crud.get_all_form_input()
        if not self.crud.validate_email(self.crud.entries["email"].get()):
            self.crud.show_toast("Το email δεν είναι σωστό.")
            return False

        if not self.crud.validate_number(self.crud.entries["phone"].get()):
            self.crud.show_toast("Το τηλέφωνο δεν είναι σωστό.")
            return False
        input[2] = self.crud.format_phone_number(self.crud.entries["phone"].get())

        if not self.crud.validate_number(self.crud.entries["mobile"].get()):
            self.crud.show_toast("Το κινητό δεν είναι σωστό.")
            return False
        input[3] = self.crud.format_phone_number(self.crud.entries["mobile"].get())

        return input

    def create_entry_in_db(self, data):
        if data:
            query = """INSERT INTO associate 
                                    (last_name, first_name, phone, mobile, email, description)
                                    VALUES (%s, %s, %s, %s, %s, %s);"""
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
        """ Updates the selected supplier entry according to the information input by the user. """
        if data and self.crud.selectedRowValues:
            associateID = self.crud.selectedRowValues[0]
            query = """ UPDATE associate 
                                SET last_name = %s, first_name = %s, phone = %s, mobile = %s, email = %s, description = %s
                                WHERE associate.id = """ + str(associateID) + ";"
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