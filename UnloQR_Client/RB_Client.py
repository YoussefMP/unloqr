from server_comms import Client
from GUI import GUIManager
from threading import Thread
from PIL import Image, ImageTk


if __name__ == "__main__":

    client = Client()
    client.connect_to_server()

    server_listener = Thread(target=client.request_id)
    server_listener.start()
    server_listener.join()

    window = GUIManager(client)





