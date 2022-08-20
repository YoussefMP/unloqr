from tkinter import Tk, Label, Frame, Button, Grid, Toplevel, StringVar, Entry
from PIL import Image, ImageTk
from os import path
import time
import urllib.request
from threading import Thread


def is_connected(host='http://google.com'):
    try:
        urllib.request.urlopen(host)
        return True
    except urllib.error.HTTPError or urllib.error.URLError as err:
        return False


class GUIManager:
    def __init__(self, client):
        
        self.client = client
        did = self.client.c_man.get_my_id()
        
        self.window = Tk()
        main_frame = Frame(self.window)
        main_frame.configure(bg="white")

        if is_connected():
            self.icon = Image.open("./static/WiFiIcon.png")
        else:
            self.icon = Image.open("./static/NoInternetIcon.png")

        mid_frame = Frame(main_frame)
        mid_frame.grid(row=2, column=1)
        mid_frame.configure(bg="white")
        mid_frame.place(in_=main_frame, anchor="center", relx=0.5, rely=0.5)

        wifi_icon = ImageTk.PhotoImage(self.icon)
        self.wifi_label = Label(main_frame, image=wifi_icon)
#        self.wifi_label = Label(main_frame, text="Here")
        self.wifi_label.configure(bg="white")
        self.wifi_label.grid(row=0, column=5, sticky="NE")
#        self.wifi_label.pack(anchor="e")
#        connection_status_thread = Thread(target=self.update_status())

        gear_icon = ImageTk.PhotoImage(Image.open("./static/GearIcon80.png"))
        man_open_btn = Button(main_frame, image=gear_icon, command=self.open_manually)
        man_open_btn.configure(bg="white")
        man_open_btn.grid(row=0, column=4, pady=(20, 0), sticky="NE")
#        man_open_btn.pack(anchor="e")

        Grid.columnconfigure(main_frame, 3, weight=1)
        
        while not path.exists("./_Config/ID_Code.png"):
            time.sleep(2)

        img = Image.open("./_Config/ID_Code.png")
        photo = ImageTk.PhotoImage(img)

        label = Label(mid_frame, image=photo)
        label.pack()
        label_text = Label(mid_frame, text=did, font='Times 32')
        label_text.configure(bg="white")
        label_text.pack()

        main_frame.pack(fill="both", expand=True, padx=20, pady=5)
        # self.window.attributes("-fullscreen", True)

        self.window.geometry("600x400")
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.configure(bg="white")
        self.window.mainloop()
        self.window.quit()

    def update_status(self):
        connection_status_update = self.window.after(5000, self.update_status)
        if is_connected():
            self.icon = Image.open("./static/WiFiIcon.png")
            text = "WIFI_ON"
        else:
            text = "WIFI_OFF"
            self.icon = Image.open("./static/NoInternetIcon.png")
        
        wifi_icon = ImageTk.PhotoImage(self.icon)
        self.wifi_label.config(image=wifi_icon)
        self.window.update_idletasks()
        
    def on_closing(self):
        self.client.disconnect()
        
    def open_manually(self):
        self.win = Toplevel()
        win.geometry("350x75")
        
        win.wm_title("Admin access")
        
        password_label = Label(win, text="Admin Passwort:")
        password_label.grid(row=0, column=0, padx=(5, 5))
    
        self.password_txt = StringVar()
        self.password_box = Entry(win, textvariable=self.password_txt, show="*")
        self.password_box.grid(row=0, column=1, padx=(0, 5))
        Grid.columnconfigure(win, 1, weight=1)
        
        submit_btn = Button(win, text="Öffnen", command=lambda: self.client.request_man_open(self.password_txt.get()))
        submit_btn.grid(row=0, column=3, padx=(0, 5))
        