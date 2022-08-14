from tkinter import Tk, Label, Frame
from PIL import Image, ImageTk
from os import path
import time
import urllib.request
from threading import Thread


def is_connected(host='http://google.com'):
    try:
        urllib.request.urlopen(host)
        return True
    except urllib.error.HTTPError as err:
        return False


class GUIManager:
    def __init__(self, did):
        self.window = Tk()
        main_frame = Frame(self.window)

        if is_connected():
            self.icon = Image.open("./static/WiFiIcon.png")
        else:
            self.icon = Image.open("./static/NoInternetIcon.png")

        mid_frame = Frame(main_frame)
        mid_frame.grid(row=2, column=1)
        mid_frame.place(in_=main_frame, anchor="center", relx=0.5, rely=0.5)

        wifi_icon = ImageTk.PhotoImage(self.icon)
        wifi_label = Label(main_frame, image=wifi_icon)
        wifi_label.pack(anchor="e")

        connection_status_thread = Thread(target=self.update_status())

        while not path.exists("./_Config/ID_Code.png"):
            time.sleep(2)

        img = Image.open("./_Config/ID_Code.png")
        photo = ImageTk.PhotoImage(img)

        label = Label(mid_frame, image=photo)
        label.pack()

        label_text = Label(mid_frame, text=did, font='Times 32')
        label_text.pack()

        main_frame.pack(fill="both", expand=True, padx=20, pady=5)
        # self.window.attributes("-fullscreen", True)

        self.window.geometry("600x400")
        self.window.mainloop()

    def update_status(self):
        connection_status_update = self.window.after(2000, self.update_status)
        if is_connected():
            self.icon = Image.open("./static/WiFiIcon.png")
        else:
            self.icon = Image.open("./static/NoInternetIcon.png")

        self.window.update_idletasks()
