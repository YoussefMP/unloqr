from ServerHandler import handle_server_messages
from Client_FileIO import ConfigManager
from os import path
import threading
import requests
import socketio


client = socketio.Client()


class Client:

    def __init__(self):
        self.c_man = ConfigManager("./_Config")
        self.server_url = "http://127.0.0.1:5000"

        print("Connecting to server...")
        client.connect(self.server_url)

    @client.event
    def request_id(self):
        """
        On app's first start this method will request ID for device from server
        :return: True, if server accepted request and sends ID back
        """
        my_id = self.c_man.get_my_id()
        data = {"id": my_id}

        def set_id_in_config(idx):
            """
            This function calls the FileIO to set up the config file on receiving new_id.
            :param idx: New ID received from the server or None
            """
            if idx != "XXXX":
                self.c_man.initialize_config_file(idx)

        client.emit("get_ID", data, callback=set_id_in_config)


def open_com_chanel(cl):
    print("Say hello")
    cl.request_id()
