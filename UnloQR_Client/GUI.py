from tkinter import Tk, Label, Frame, Button, Grid, Toplevel, StringVar, Entry

import socketio.exceptions
from PIL import Image, ImageTk
from os import path
import time
import urllib.request
from threading import Thread
import socket


def is_connected(host='http://unloqr.herokuapp.com'):
    try:
        print(urllib.request.urlopen(host))
        return True
    except Exception as err:
        print(err)
        return False



class GUIManager:
    def __init__(self, client):
        
        self.client = client
        did = self.client.c_man.get_my_id()
        self.client.did = did

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

        self.server_update = StringVar()
        self.wifi_label = Label(main_frame, textvariable=self.server_update)
        self.wifi_label.configure(bg="white")
        self.wifi_label.grid(row=0, column=2, sticky="NE")

        wifi_icon = ImageTk.PhotoImage(self.icon)
        self.wifi_label = Label(main_frame, image=wifi_icon)
        self.wifi_label.configure(bg="white")
        self.wifi_label.grid(row=0, column=5, sticky="NE")

        connection_status_thread = Thread(target=self.update_status)
        connection_status_thread.start()

        gear_icon = ImageTk.PhotoImage(Image.open("./static/GearIcon80.png"))
        man_open_btn = Button(main_frame, image=gear_icon, command=self.open_manually)
        man_open_btn.configure(bg="white")
        man_open_btn.grid(row=0, column=4, pady=(20, 0), sticky="NE")

        Grid.columnconfigure(main_frame, 3, weight=1)
        
        while not path.exists("./_Config/ID_Code.png"):
            time.sleep(2)

        img = Image.open("./_Config/ID_Code.png")
        photo = ImageTk.PhotoImage(img)

        label = Label(mid_frame, image=photo)
        label.pack()

        self.id_text = StringVar()
        self.id_text.set(did)
        label_text = Label(mid_frame, textvariable=self.id_text, font='Times 32')
        label_text.configure(bg="white")
        label_text.pack()
        id_update = Thread(target=self.update_id_label())

        main_frame.pack(fill="both", expand=True, padx=20, pady=5)
        # self.window.attributes("-fullscreen", True)

#        self.window.geometry("600x400")
        self.window.state("zoomed")
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.configure(bg="white")
        self.window.mainloop()
        self.window.quit()

    def get_client(self):
        return self.client

    def on_closing(self):
        print("DEFINING DICONNECT")
        try:
            self.client.on_disconnect()
        except socketio.exceptions.BadNamespaceError:
            print("Server is out")
        self.window.destroy()

    def open_manually(self):
        self.win = Toplevel()
        self.win.geometry("350x50")
        
        self.win.wm_title("Admin access")
        
        password_label = Label(self.win, text="Admin Passwort:")
        password_label.grid(row=0, column=0, padx=(5, 5))
    
        self.password_txt = StringVar()
        password_box = Entry(self.win, textvariable=self.password_txt, show="*")
        password_box.grid(row=0, column=1, padx=(0, 5))
        Grid.columnconfigure(self.win, 1, weight=1)
        
        submit_btn = Button(self.win, text="Öffnen", command=self.close_modal)
        submit_btn.grid(row=0, column=3, padx=(0, 5))

    def close_modal(self):
        self.client.request_man_open(self.password_txt.get())
        self.win.destroy()
        self.win.update()

    def update_status(self):
        connection_status_update = self.window.after(3500, self.update_status)
        if is_connected():
            self.icon = Image.open("./static/WiFiIcon.png")
            self.wifi_label.grid(pady=(0, 0), padx=(0, 0))
        else:
            self.icon = Image.open("./static/NoInternetIcon.png")
            self.wifi_label.grid(pady=(10, 0), padx=(10, 0))

        wifi_icon = ImageTk.PhotoImage(self.icon)
        self.wifi_label.configure(image=wifi_icon)
        self.wifi_label.image = wifi_icon

        self.window.update_idletasks()

    def update_id_label(self):
        update_id_label = self.window.after(2000, self.update_id_label)

        print("Hello from id label")
        did = self.client.c_man.get_my_id()
        if did != "XXXX":
            self.client.did = did
            self.id_text.set(did)
            self.window.update_idletasks()
            self.window.after_cancel(update_id_label)

