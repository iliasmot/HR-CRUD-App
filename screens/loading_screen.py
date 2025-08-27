import tkinter as tk
from tkinter import ttk

class LoadingScreen(tk.Frame):
    """
    This class is a subclass of tk.Frame and serves as a loading screen. There is a known Tkinter bug that briefly
    displays the last initialized frame at startup before the desired frame loads. To work around this, LoadingScreen is
    initialized last, ensuring a seamless transition and preventing Tkinter from displaying any other frame, which
    might contain restricted access or sensitive information
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        titleLabel = ttk.Label(self, text="placeholder", font=(controller.defaultTxtFont, 50))
        loadingTxt = ttk.Label(self, text="Παρακαλώ περιμένετε...", font=(controller.defaultTxtFont, controller.defaultTxtSize))
        titleLabel.pack(pady=50)
        loadingTxt.pack()