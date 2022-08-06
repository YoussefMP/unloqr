from server_comms import Client, open_com_chanel
from GUI import GUIManager
from threading import Thread


if __name__ == "__main__":

    client = Client()
    server_listener = Thread(target=open_com_chanel, args=[client])
    server_listener.start()

    window = GUIManager(client.c_man.get_my_id())





