import tkinter as tk
from tkinter import *
import json
BTN_IMAGE = "./Images/GUI - btn login.png"
BG_IMAGE = "./Images/GUI - BG Login.png"
FONT = "Calibri"
FONT_BUTTON = (FONT,14)


class CLoginGUI:

    def __init__(self, parent_wnd, callback_register, callback_signin) -> None:

        # set windows hierarchy
        self._parent_wnd = parent_wnd
        self._this_wnd = tk.Toplevel(parent_wnd)
        self._this_wnd.title("Login")

        self._canvas = None
        self._img_bg = None
        self._img_btn = None

        self._entry_login = None
        self._entry_pw = None

        self._btn_register = None
        self._btn_signin = None

        # data fo r the registration
        self._login = ''
        self._pw = ''
        self.callback_register = callback_register
        self.callback_signin = callback_signin


        self.create_ui()

    def get_login(self) -> str:
        return self._login

    def get_pw(self) -> str:
        return self._pw

    def create_ui(self):

        # Load bg image
        self._img_bg:PhotoImage = PhotoImage(file=BG_IMAGE)
        img_width = self._img_bg.width()
        img_height = self._img_bg.height()

        # Set size of the application window = image size
        self._this_wnd.geometry(f'{img_width}x{img_height}')
        self._this_wnd.resizable(False,False)

        # Create a canvas to cover the entire window
        self._canvas = tk.Canvas(self._this_wnd, width=img_width, height=img_height)
        self._canvas.pack(fill='both', expand=True)
        self._canvas.create_image(0, 0, anchor="nw", image=self._img_bg)

        # Add labels, the same as.. add text on canvas
        self._canvas.create_text(30,40,text='Login:',font=FONT_BUTTON,fill='#000000',anchor='w')
        self._canvas.create_text(30,120,text='Password:',font=FONT_BUTTON,fill='#000000',anchor='w')
        
        
        # Load button image
        self._img_btn = PhotoImage(file=BTN_IMAGE)
        img_btn_w = self._img_btn.width()
        img_btn_h = self._img_btn.height()

        # Button "Register"
        self._btn_register = tk.Button(self._canvas,text="Register",font=FONT_BUTTON,fg="#c0c0c0",compound="center",
                                       width=img_btn_w,height=img_btn_h,image=self._img_btn,bd=0,
                                       command=self.on_click_register)
        self._btn_register.place(x=330,y=30)

        # Button "SignIn"
        self._btn_signin:Button = tk.Button(self._canvas,text="SignIn",font=FONT_BUTTON,fg="#c0c0c0",compound="center",
                                     width=img_btn_w,height=img_btn_h,image=self._img_btn,bd=0,
                                     command=self.on_click_signin)
        self._btn_signin.place(x=330,y=70)


        # Create Entry boxes
        self._entry_login = tk.Entry(self._canvas,font=('Calibri',16),fg='#808080',)
        self._entry_login.insert(0,'')
        self._entry_login.place(x=30,y=60)

        self._entry_pw = tk.Entry(self._canvas,font=('Calibri',16),fg='#808080')
        self._entry_pw.insert(0,"")
        self._entry_pw.place(x=30,y=140)

    def run(self) -> None:
        self._this_wnd.mainloop()

    def on_click_register(self) -> None:
        self._login = self._entry_login.get()
        self._pw = self._entry_pw.get()
        data = json.dumps({"login": self._login, "password": self._pw})
        self.callback_register(data)
        

    def on_click_signin(self) -> None:
        self._login: str = self._entry_login.get()
        self._pw: str = self._entry_pw.get()
        data: str = json.dumps({"login": self._login, "password": self._pw})
        self.callback_signin(data)

if __name__ == "__main__":
    wnd = CLoginGUI(None, None, None)
    wnd.run()
