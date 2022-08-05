from server_comms import Client, open_com_chanel
from threading import Thread
from tkinter import *
import requests
import time


if __name__ == "__main__":

    client = Client()
    server_listener = Thread(target=open_com_chanel, args=[client])
    server_listener.start()

    # window = Tk()
    # window.title("Welcome")
    # window.mainloop()





