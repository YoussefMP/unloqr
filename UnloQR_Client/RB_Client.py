from server_comms import Client, open_com_chanel
from GUI import GUIManager
from threading import Thread
from os import path
import time


if __name__ == "__main__":

    client = Client()
    server_listener = Thread(target=client.request_id)
    server_listener.start()
    server_listener.join()

#    while not path.exists("./_Config/config.ini"):
        
#    time.sleep(1)
    
    window = GUIManager(client)





