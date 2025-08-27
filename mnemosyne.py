import os
import sys
import tkinter as tk
from tkinter import ttk

from database_connection import Database

from screens.associate_crud_screen import AssociateCRUDScreen
from screens.employee_search_screen import EmployeeSearchScreen
from screens.home_screen import HomeScreen
from screens.loading_screen import LoadingScreen
from screens.log_in_screen import LogInScreen
from old.search_screen import SearchScreen
from screens.it_employee_search_screen import ITEmployeeSearchScreen
from screens.hr_employee_search_screen import HREmployeeSearchScreen
from screens.supplier_crud_screen import SupplierCRUDScreen
from screens.employee_crud_screen import EmployeeCRUDScreen

class App(tk.Tk):
    """
    Desktop Application to aid in retrieving information on a company's employees.
    I.M.
    """
    def __init__(self):
        super().__init__()
        self.title("Τηλεφωνικός Κατάλογος")
        self.geometry("1300x750")

        # make sure the path is valid for both development and executable
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        theme_path = os.path.join(base_path, "Forest-ttk-theme-master", "forest-light.tcl") # useing an external theme

        self.tk.call('source', theme_path)  # load theme
        ttk.Style().theme_use('forest-light')  # apply theme

        # setting some general values for the ui
        self.defaultTxtSize = 12
        self.defaultTitleSize = 20
        self.defaultTxtFont = "Century Gothic"
        self.style = ttk.Style()
        self.style.configure("Big.TButton", anchor="center", font=(self.defaultTxtFont, self.defaultTxtSize))
        self.style.configure("BigText.TButton", anchor="center", font=(self.defaultTxtFont, 30))

        # initialising database
        self.database = Database("000.00.00.00", "user", "password", "databasename") # change to server info on release!!!
        self.database.connect()

        # variables for user identification
        self.userType = ""
        self.generalUserPass = ""
        self.itUserPass = ""
        self.managementUserPass = ""
        self.adminUserPass = ""


        # a container frame for all other frames ("screens") of the app
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        # row and column weights of the container
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {} # Dictionary to hold all the app frames

        # initialising all frames
        for Screen in (LogInScreen, HomeScreen, SearchScreen, EmployeeSearchScreen, ITEmployeeSearchScreen, EmployeeCRUDScreen,
                       SupplierCRUDScreen, AssociateCRUDScreen, HREmployeeSearchScreen, LoadingScreen): # make sure LoadingScreen is last
            screenName = Screen.__name__
            frame = Screen(parent=container, controller=self)
            self.frames[screenName] = frame # inserting page to the dictionary
            frame.grid(row=0, column=0, sticky="nsew")

        self.get_all_user_credentials()

        self.show_frame("LogInScreen")

    # methods
    def show_frame(self, screen_name):
        """ Brings the desired frame to the front. Accepts the class' name (string)."""
        frame = self.frames[screen_name]
        if hasattr(frame, "update"):
            frame.update()  # keep the frame up to date if a method exists
        frame.tkraise()

    def get_database(self):
        """ Give access to the database connection."""
        return self.database

    def on_closing(self):
        """ Handles app closing event making sure to disconnect the database. """
        try:
            self.database.disconnect()
            self.destroy()
        except Exception as e:
            self.destroy()

    def get_all_user_credentials(self):
        " Fetches all credentials for all users from the database and puts them in the appropriate instance variables."
        database = self.get_database().get_connection()
        try:
            cursor = database.cursor()
            # general users
            query = "SELECT user_password FROM app_user WHERE username = 'employee';"
            cursor.execute(query)
            self.generalUserPass = cursor.fetchone()[0]

            # it employees
            query = "SELECT user_password FROM app_user WHERE username = 'it_employee';"
            cursor.execute(query)
            self.itUserPass = cursor.fetchone()[0]

            # management
            query = "SELECT user_password FROM app_user WHERE username = 'management';"
            cursor.execute(query)
            self.managementUserPass = cursor.fetchone()[0]

            # admin
            query = "SELECT user_password FROM app_user WHERE username = 'admin';"
            cursor.execute(query)
            self.adminUserPass = cursor.fetchone()[0]
        except Exception as e:
            self.generalUserPass = "null"
            self.itUserPass = "null"
            self.managementUserPass = "null"
            self.adminUserPass = "null"


# run the app
if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
