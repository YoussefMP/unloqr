from server_comms import Client, open_com_chanel
from GUI import GUIManager
from threading import Thread
from os import path
import time


if __name__ == "__main__":

    client = Client()
    server_listener = Thread(target=open_com_chanel, args=[client])
    server_listener.start()

    while not path.exists("./_Config/config.ini"):
        time.sleep(1)
    window = GUIManager(client.c_man.get_my_id())





