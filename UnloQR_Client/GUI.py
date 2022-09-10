from tkinter import Tk, Label, Frame, Button, Grid, Toplevel, StringVar, Entry
import socketio.exceptions
from os import path
import time
import http.client as httplib
from threading import Thread
import psutil
import os
try:
    import RPi.GPIO as GPIO
    __raspberry__ = True
except ModuleNotFoundError:
    __raspberry__ = False
from PIL import Image, ImageTk

break_all = False


def is_connected():
    conn = httplib.HTTPSConnection("8888.google", timeout=5)
    try:
        conn.request("HEAD", "/")
        return True
    except Exception:
        return False
    finally:
        conn.close()


class GUIManager:
    def __init__(self, client):
        
        self.client = client
        did = self.client.c_man.get_my_id()
        self.client.did = did

        self.window = Tk()
        main_frame = Frame(self.window)
        main_frame.configure(bg="white")

        if is_connected():
            self.icon = Image.open("/home/pi/Desktop/unloqr/UnloQR_Client/static/WiFiIcon.png")
        else:
            self.icon = Image.open("/home/pi/Desktop/unloqr/UnloQR_Client/static/NoInternetIcon.png")

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

        gear_icon = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/unloqr/UnloQR_Client/static/GearIcon80.png"))
        man_open_btn = Button(main_frame, image=gear_icon, command=self.open_manually)
        man_open_btn.configure(bg="white")
        man_open_btn.grid(row=0, column=4, pady=(20, 0), sticky="NE")
        
        Grid.columnconfigure(main_frame, 2, weight=1)
        
        while not path.exists("/home/pi/Desktop/unloqr/UnloQR_Client/_Config/ID_Code.png"):
            time.sleep(2)

        lock_icon = ImageTk.PhotoImage(Image.open("/home/pi/Desktop/unloqr/UnloQR_Client/static/LockIconFull80.png"))
        close_btn = Button(mid_frame, image=lock_icon, command=self.close_lock)
        close_btn.configure(bg="white")
        close_btn.pack(pady=(0, 35))

        img = Image.open("/home/pi/Desktop/unloqr/UnloQR_Client/_Config/ID_Code.png")
        photo = ImageTk.PhotoImage(img)

        label = Label(mid_frame, image=photo)
        label.pack()

        self.id_text = StringVar()
        self.id_text.set(did)
        label_text = Label(mid_frame, textvariable=self.id_text, font='Times 32')
        label_text.configure(bg="white")
        label_text.pack()
        id_update = Thread(target=self.update_id_label())

        check_comms_btn = Button(mid_frame, text="Aktualisieren", command=self.client.check_connection)
        check_comms_btn.pack()
        
        self.server_ans = StringVar()
        self.server_ans.set("SERVER....")
        server_ans_label = Label(mid_frame, textvariable=self.server_ans, font='Times 22')
        server_ans_label.configure(bg="white")
        server_ans_label.pack()
        serv_ans_thread = Thread(target=self.update_serv_ans)
        serv_ans_thread.start()

        main_frame.pack(fill="both", expand=True, padx=20, pady=5)
        
        self.window.attributes("-fullscreen", True)
        #self.window.geometry("800x600")
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.configure(bg="white")
        self.window.mainloop()
        self.window.quit()

    def get_client(self):
        return self.client

    def on_closing(self):
        print("Closing the app...")
        try:
            self.client.break_all = True
            self.client.on_disconnect()
        except socketio.exceptions.BadNamespaceError:
            print("Server is out")
        self.window.destroy()
        psutil.Process(os.getpid()).terminate()

    def open_manually(self):
        self.win = Toplevel()
        self.win.geometry("400x100")
        
        self.win.wm_title("Admin access")
        
        password_label = Label(self.win, text="Admin Passwort:")
        password_label.grid(row=0, column=0, padx=(5, 5))
    
        self.password_txt = StringVar()
        password_box = Entry(self.win, textvariable=self.password_txt, show="*")
        password_box.grid(row=0, column=1, padx=(0, 5))
        Grid.columnconfigure(self.win, 1, weight=1)
        
        submit_btn = Button(self.win, text="Öffnen", command=self.close_modal)
        submit_btn.grid(row=0, column=3, padx=(0, 5), sticky="NE")
        
        close_app_btn = Button(self.win, text="App schließen", command=self.close_app)
        close_app_btn.grid(row=1, column=3, sticky="NE")

    def close_modal(self):
        self.client.request_man_open(self.password_txt.get())
        self.win.destroy()
        self.win.update()
        
    def close_app(self):
        self.client.break_all = True
        self.client.request_close_app(self.password_txt.get())
        self.win.destroy()
        self.win.update()

    def update_serv_ans(self):
        connection_status_update = self.window.after(2000, self.update_serv_ans)
        self.server_ans.set(self.client.server_ans)
        self.window.update_idletasks()
        
    def update_status(self):
        connection_status_update = self.window.after(5000, self.update_status)
        
        print(f"status ===>  {self.client.break_all}")
        if self.client.break_all:
            self.on_closing()
    
        if is_connected():
            self.icon = Image.open("/home/pi/Desktop/unloqr/UnloQR_Client/static/WiFiIcon.png")
            self.wifi_label.grid(pady=(0, 0), padx=(0, 0))
        else:
            self.icon = Image.open("/home/pi/Desktop/unloqr/UnloQR_Client/static/NoInternetIcon.png")
            self.wifi_label.grid(pady=(10, 0), padx=(10, 0))

        wifi_icon = ImageTk.PhotoImage(self.icon)
        self.wifi_label.configure(image=wifi_icon)
        self.wifi_label.image = wifi_icon

        self.window.update_idletasks()

    def update_id_label(self):
        update_id_label = self.window.after(2000, self.update_id_label)

        did = self.client.c_man.get_my_id()
        if did != "XXXX":
            self.client.did = did
            self.id_text.set(did)
            self.window.update_idletasks()
            self.window.after_cancel(update_id_label)

    def close_lock(self):
        self.client.server_ans = "Sie Können den QR-Code wieder scannen"
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(13, GPIO.OUT)
        GPIO.output(13, 0)