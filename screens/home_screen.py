import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import win32com.client


class HomeScreen(tk.Frame):
    """
    HomeScreen is a tkinter Frame that works as the main screen for the specific users.
    In this screen users can view employees' birthdays that occur on the current day as
    well as people who celebrate their name day. Additionally, there are buttons for logging
    out (and returning to the LogInScreen) and for being redirected to the SearchScreen
    -I.M. - 2025
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # get today and next couple of days' dates
        self.today = datetime.today().strftime('%d/%m')
        self.tomorrow = (datetime.today() + timedelta(days=1)).strftime('%d/%m')
        self.dayAfterTomorrow = (datetime.today() + timedelta(days=2)).strftime('%d/%m')

        self.birthdayAddresses = ""
        self.namedayAddresses = ""

        # initialising ui elements
        self.titleLabel = ttk.Label(self, text="ΕΟΡΤΟΛΟΓΙΟ", font=(controller.defaultTxtFont, controller.defaultTitleSize))
        self.todaysCelebrationsLabel = ttk.Label(self, text="• Γιορτές Σήμερα •",
                                                 font=(controller.defaultTxtFont, controller.defaultTxtSize), justify="center")
        self.tomorrowsCelebrationsLabel = ttk.Label(self, text="• Γιορτές Αύριο •",
                                                 font=(controller.defaultTxtFont, controller.defaultTxtSize), justify="center")
        self.dayAfterTomorrowCelebrationsLabel = ttk.Label(self, text="• Γιορτές Μεθαύριο •",
                                                 font=(controller.defaultTxtFont, controller.defaultTxtSize), justify="center")
        # self.logOutButton = ttk.Button(self, text="Αποσύνδεση", style="Big.TButton", command=lambda: controller.show_frame("LogInScreen"))
        self.frameForButtons = ttk.Frame(self)
        self.frameForButtons.columnconfigure(0, weight=1)
        self.frameForButtons.columnconfigure(1, weight=1)
        self.frameForButtons.columnconfigure(2, weight=1)

        self.goToSearchScreenButton = ttk.Button(self.frameForButtons, text="Προσωπικό", style="Big.TButton",
                                                 command=self.redirect_based_on_user_type, width=50)
        self.goToSupplierSearchScreenButton = ttk.Button(self.frameForButtons, text="Προμηθευτές", style="Big.TButton",
                                                         command=lambda: controller.show_frame("SupplierCRUDScreen"), width=50)
        self.goToAssociateSearchScreenButton = ttk.Button(self.frameForButtons, text="Συνεργάτες", style="Big.TButton",
                                                          command=lambda: controller.show_frame("AssociateCRUDScreen"), width=50)

        # table for today's celebrations
        self.celebrationTableToday = ttk.Treeview(self, columns=("birthdays", "name_days"), show="headings", height=7)
        self.celebrationTableToday.heading("birthdays", text="Γενέθλια")
        self.celebrationTableToday.heading("name_days", text="Εορτές")
        self.celebrationTableToday.column("birthdays", width=300, anchor="center")
        self.celebrationTableToday.column("name_days", width=300, anchor="center")

        # table for tomorrow's celebrations
        self.celebrationTableTomorrow = ttk.Treeview(self, columns=("birthdays", "name_days"), show="headings", height=5)
        self.celebrationTableTomorrow.heading("birthdays", text="Γενέθλια")
        self.celebrationTableTomorrow.heading("name_days", text="Εορτές")
        self.celebrationTableTomorrow.column("birthdays", width=300, anchor="center")
        self.celebrationTableTomorrow.column("name_days", width=300, anchor="center")

        # table for the day after tomorrow's celebrations
        self.celebrationTableDATomorrow = ttk.Treeview(self, columns=("birthdays", "name_days"), show="headings", height=3)
        self.celebrationTableDATomorrow.heading("birthdays", text="Γενέθλια")
        self.celebrationTableDATomorrow.heading("name_days", text="Εορτές")
        self.celebrationTableDATomorrow.column("birthdays", width=300, anchor="center")
        self.celebrationTableDATomorrow.column("name_days", width=300, anchor="center")

        self.update_celebration_widgets()

        self.create_header("Εορτολόγιο", "")

        self.sendWishesButton = ttk.Button(self, text="Αποστολή e-mail", style="Big.TButton", command=self.send_wishes_on_click) # 📧 📩

        self.pack_header()
        # placing elements in the ui
        self.titleLabel.pack(pady=10)
        self.todaysCelebrationsLabel.pack()
        self.celebrationTableToday.pack()
        # hide other days for now...
        # self.tomorrowsCelebrationsLabel.pack()
        # self.celebrationTableTomorrow.pack()
        # self.dayAfterTomorrowCelebrationsLabel.pack()
        # self.celebrationTableDATomorrow.pack()
        self.sendWishesButton.pack(pady=10)
        self.frameForButtons.pack(pady=50, padx=100)
        self.goToSearchScreenButton.grid(row=0, column=0, padx=5)
        self.goToSupplierSearchScreenButton.grid(row=0, column=1, padx=5)
        self.goToAssociateSearchScreenButton.grid(row=0, column=2, padx=5)
        # self.logOutButton.pack(pady=50)

    # U. I.
    def create_header(self, headerTitle, previousPageTitle):
        self.header = ttk.Frame(self)
        self.header.columnconfigure(0, weight=1)
        self.header.columnconfigure(1, weight=1)
        self.header.columnconfigure(2, weight=1)


        self.logOutButton = ttk.Button(self.header, style="Big.TButton", text="Αποσύνδεση",
                                       command=lambda: self.controller.show_frame("LogInScreen"))
        # self.screenTitle = ttk.Label(self.header, text=headerTitle, font=(self.controller.defaultTxtFont, self.controller.defaultTitleSize))

    def pack_header(self):
        self.header.pack(fill="x")
        # self.screenTitle.grid(row=0, column=1, padx="320")
        self.logOutButton.grid(row=0, column=2, sticky="e", padx="10")

    # Celebrations and Wishes

    def update_celebration_widgets(self):
        """ Updates all """
        self.celebrationTableToday.configure(height=self.populate_widget(self.celebrationTableToday, self.today))
        self.celebrationTableTomorrow.configure(height=self.populate_widget(self.celebrationTableTomorrow, self.tomorrow))
        self.celebrationTableDATomorrow.configure(height=self.populate_widget(self.celebrationTableDATomorrow, self.dayAfterTomorrow))

    def search_db_for_celebrations(self, celebration, date):
        queryText = f"""SELECT employee.first_name, employee.last_name FROM employee
                    WHERE employee.{celebration} = "{date}";"""

        # connect to database
        database = self.controller.get_database().get_connection()
        try:
            cursor = database.cursor()
            cursor.execute(queryText)
            return cursor.fetchall()
        except Exception as e:
            return "none"

    def populate_widget(self, celebrationWidget, date):
        """ Fills the Birthday and Name Day tree with people's names while making sure to align them properly.
        Returns the maximum amount of rows that were inserted to the tree view"""

        # getting appropriate messages for no entries found
        noResultsMsgBday = "Κανείς δεν έχει γενέθλια "
        noResultsMsgNday = "Κανείς δεν έχει γιορτή "
        if date == self.today:
            noResultsMsgBday += "σήμερα."
            noResultsMsgNday += "σήμερα."
        elif date == self.tomorrow:
            noResultsMsgBday += "αύριο."
            noResultsMsgNday += "αύριο."
        elif date == self.dayAfterTomorrow:
            noResultsMsgBday += "μεθαύριο."
            noResultsMsgNday += "μεθαύριο."
        else:
            noResultsMsgBday += "."
            noResultsMsgNday += "."

        # fetching people who celebrate today
        birthday_results = self.search_db_for_celebrations("birthday", date)
        name_day_results = self.search_db_for_celebrations("name_day", date)

        if birthday_results == "none" or name_day_results == "none":
            celebrationWidget.insert("", "end", values=("error", "error"))
        else:
        # getting the length of the longest list of people and the shortest
            max_length = max(len(birthday_results), len(name_day_results))
            min_length = min(len(birthday_results), len(name_day_results))

            # next we need to manage the results in order to have a clean looking UI

            # in case of the two lists not being equal
            if not len(birthday_results) == len(name_day_results):
                for i in range(max_length): # iterate over the longer of the two
                    if i < min_length: # while both lists have still items
                        column1txt = f" {birthday_results[i][0]} {birthday_results[i][1]}\n" # bday celebrator
                        column2txt = f" {name_day_results[i][0]} {name_day_results[i][1]}\n" # nday celebrator
                        celebrationWidget.insert("", "end", values=(column1txt, column2txt)) # put them in the table
                    else: # when the shorter list runs out we have to replace its text with empty strings
                        if len(name_day_results) == min_length: # if the name list is the short one
                            column1txt = f" {birthday_results[i][0]} {birthday_results[i][1]}\n" # display birthdays
                            column2txt = "" # empty field
                            # vvv-- check if the short list is actually empty and this is its first entry to the table
                            if min_length == 0 and i == 0: column2txt = noResultsMsgNday # Then display an appropriate message
                        if len(birthday_results) == min_length: # if the birthday list is the short one
                            column1txt = "" # empty field
                            column2txt = f" {name_day_results[i][0]} {name_day_results[i][1]}\n" # display name days
                            if min_length == 0 and i == 0: column1txt = noResultsMsgBday # similar logic as above
                        # finally display the entries
                        celebrationWidget.insert("", "end", values=(column1txt, column2txt))
            else: # if the lists are equal
                if not birthday_results: # if they are both empty
                    celebrationWidget.insert("", "end", values=(noResultsMsgBday, noResultsMsgNday))
                else:
                    for i in range(max_length):
                        column1txt = f" {birthday_results[i][0]} {birthday_results[i][1]}\n"
                        column2txt = f" {name_day_results[i][0]} {name_day_results[i][1]}"
                        celebrationWidget.insert("", "end", values=(column1txt, column2txt))
            return max_length

    def send_wishes_on_click(self):
        if self.fetch_celebration_addresses("birthday"):
            self.send_wishes("birthday", self.fetch_celebration_addresses("birthday"))
        if self.fetch_celebration_addresses("name_day"):
            self.send_wishes("name_day", self.fetch_celebration_addresses("name_day"))
        self.set_today_as_last_email_sent_date()
        self.update()

    def send_wishes(self, celebration, contacts):
        # Start Outlook
        outlook = win32com.client.Dispatch("Outlook.Application")
        mail = outlook.CreateItem(0)  # 0 means a new mail item

        # Set email fields
        mail.BCC = contacts

        if celebration == "birthday":
            mail.Subject = "🎂 Ευχές Γενεθλίων"
            mail.Body = """Χρόνια πολλά! 
Σας ευχόμαστε πολλά χρόνια γεμάτα υγεία, χαρά και επιτυχία σε κάθε σας στόχο, τόσο προσωπικό όσο και επαγγελματικό. 
Ευχόμαστε τα γενέθλιά σας σήμερα να είναι μια ημέρα υπέροχη, γεμάτη χαμόγελα!
        
-Το Τμήμα Πληροφορικής 🎂"""

        elif celebration == "name_day":
            mail.Subject = "🎁 Γιορτινές Ευχές"
            mail.Body = """Χρόνια πολλά για την ονομαστική σας εορτή! 
Σας ευχόμαστε υγεία, ευτυχία και πολλές όμορφες στιγμές.
Ευχόμαστε η γιορτή σας σήμερα να είναι μια όμορφη ημέρα γεμάτη χαρές! 

-Το Τμήμα Πληροφορικής 🎁"""

        # Display the email for review. The user must send it manually
        mail.Display()

    def fetch_celebration_addresses(self, celebration):
        stringToReturn = ""
        queryText = f"""SELECT employee.business_email FROM employee WHERE employee.{celebration} = "{self.today}";"""
        database = self.controller.get_database().get_connection()
        try:
            cursor = database.cursor()
            cursor.execute(queryText)
            results = cursor.fetchall()
            # convert results to a semicolon-separated string
            for result in results:
                if result[0]:
                    stringToReturn += result[0] + "; "
            return stringToReturn
        except Exception as e:
            print(f"Error fetching {celebration} addresses: {e}")
            return ""

    def check_if_already_sent_wishes_today(self):
        if self.today == self.get_last_email_sent_date():
            return True
        else:
            return False

    def get_last_email_sent_date(self):
        database = self.controller.get_database().get_connection()
        query = "SELECT last_date FROM last_sent_email_date WHERE id = 1;"
        try:
            cursor = database.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            for result in results:
                if result[0]:
                    return result[0]
                else:
                    return 0
        except Exception as e:
            print(e)

    def set_today_as_last_email_sent_date(self):
        database = self.controller.get_database().get_connection()
        query = f"""UPDATE last_sent_email_date SET last_date = "{self.today}" WHERE id = 1;"""
        try:
            cursor = database.cursor()
            cursor.execute(query)
            database.commit()
        except Exception as e:
            print(e)

    # Other:

    def redirect_based_on_user_type(self):
        if self.controller.userType == "it":
            self.controller.show_frame("ITEmployeeSearchScreen")
        elif self.controller.userType == "admin":
            self.controller.show_frame("EmployeeCRUDScreen")
    def update(self):
        if self.check_if_already_sent_wishes_today():
            self.sendWishesButton.config(state="disabled")
