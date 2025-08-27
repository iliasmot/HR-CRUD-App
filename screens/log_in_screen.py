import tkinter as tk
from tkinter import ttk


class LogInScreen(tk.Frame):
    """
    LogInScreen is a tkinter Frame that works as a Log-In screen for the application's users.
    I.M. - 2025
    """

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # initialising ui elements
        self.title = ttk.Label(self, text="• Σύνδεση •", font=(controller.defaultTxtFont, controller.defaultTitleSize))
        self.usernameEntry = ttk.Entry(self, font=(controller.defaultTxtFont, controller.defaultTxtSize))
        self.usernameLabel = ttk.Label(self, text="Username", font=(controller.defaultTxtFont, controller.defaultTxtSize))
        self.passwordEntry = ttk.Entry(self, show="•", font=(controller.defaultTxtFont, controller.defaultTxtSize))
        self.passwordEntry.bind("<Return>", lambda event:self.log_in_button_on_click(controller))
        self.passwordLabel = ttk.Label(self, text="Password", font=(controller.defaultTxtFont, controller.defaultTxtSize))
        self.logInButton = ttk.Button(self, text="Είσοδος", style="Big.TButton", command=lambda:self.log_in_button_on_click(controller))
        self.errorMsgLabel = ttk.Label(self, text="")
        self.usernameEntry.insert(0, "default") # as per request the username is never cross-referenced
            # with the database. It is there to simply give the illusion of choice... Users are verified and
            # differentiated solely through their password... The prefilled username also serves as a "tip" for the users

        # placing the ui elements
        self.title.pack(pady=30)
        self.usernameLabel.pack(pady=10)
        self.usernameEntry.pack()
        self.passwordLabel.pack(pady=10)
        self.passwordEntry.pack()
        self.logInButton.pack(pady="25")
        self.errorMsgLabel.pack()

    def log_in_button_on_click(self, controller):
        """ Starts the sequence of events necessary for the log in process"""
        if self.check_input_fields():
            if self.check_credentials(controller):
                self.set_user_type(controller)
                self.reset_input_fields()
                self.redirect_user(controller)
            else:
                self.reset_input_fields()
                self.update_error_txt("Τα στοιχεία που εισαγάγατε δεν είναι σωστά.")
        else:
            self.reset_input_fields()
            self.update_error_txt("Παρακαλώ συμπληρώστε όλα τα πεδία.")

    def check_input_fields(self):
        """ Checks for invalid entries or empty fields in username and password input """
        if self.usernameEntry.get() == "": # or self.passwordEntry.get() == "":
            return False
        else:
            return True

    def check_credentials(self, controller):
        """ Checks if the credentials given are correct by looking for them
        in the database """
        database = controller.get_database().get_connection()
        cursor = database.cursor()
        query = "SELECT user_password FROM app_user WHERE user_password =%s"
        cursor.execute(query,(self.passwordEntry.get(),))
        result = cursor.fetchone()


        # check for a match, not just a return result, because the query is not case-sensitive
        if result:
            if result[0] == self.passwordEntry.get() or self.passwordEntry.get() == "":
                return True
            else:
                return  False
        else:
            return False

    def update_error_txt(self, errorText):
        """ Updates the UI to reflect possible errors during input or
        incorrect credentials """
        self.errorMsgLabel.configure(text=errorText)

    def reset_input_fields(self):
        """ Resets username and password input fields"""
        self.usernameEntry.delete(0, tk.END)
        self.usernameEntry.insert(0, "default")
        self.passwordEntry.delete(0, tk.END)
        self.update_error_txt("")

    def redirect_user(self, controller):
        """ Redirects the user to the appropriate screen depending on their user type"""
        if controller.userType == "it" or controller.userType == "admin":
            controller.show_frame("HomeScreen")
        elif controller.userType == "general" :
            controller.show_frame("EmployeeSearchScreen")
        elif controller.userType == "management":
            controller.show_frame("HREmployeeSearchScreen")

    def set_user_type(self, controller):
        """ Sets the userType according to the credentials given by the user. This method is where the identification
        criteria are stored. """
        if self.passwordEntry.get() == controller.itUserPass:
            controller.userType = "it"
        elif self.passwordEntry.get() == controller.generalUserPass:
            controller.userType = "general"
        elif self.passwordEntry.get() == controller.adminUserPass:
            controller.userType = "admin"
        elif self.passwordEntry.get() == controller.managementUserPass:
            controller.userType = "management"

    def update(self):
        self.reset_input_fields()
