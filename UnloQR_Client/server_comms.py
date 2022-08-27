import threading
from ServerMsgHandler import response_ids, set_c_man, set_client
from Client_FileIO import ConfigManager
import socketio
import base64
import time
from flask import jsonify

client = socketio.Client()


class Client:

    def __init__(self):
        self.c_man = ConfigManager("./_Config")
        self.server_url = "https://unloqr.herokuapp.com/"
        # self.server_url = "http://127.0.0.1:5000"

        set_c_man(self.c_man)
        set_client(self)

    def connect_to_server(self):
        print("Connecting to server...")
        tries = 0
        while tries < 10:
            try:
                tries += 1
                client.connect(self.server_url, wait_timeout=15)
                break
            except ConnectionError:
                print("Caught Connection Error 1, retrying... ")
                time.sleep(1)
            except Exception as err:
                print(f"Sleeping in the finally because of {err} \n Retrying ...")
                time.sleep(2)

        print("Connected_or_not")

    @client.event
    def request_id(self):
        """
        On app's first start this method will request ID for device from server
        :return: True, if server accepted request and sends ID back
        """
        my_id = self.c_man.get_my_id()
        data = {"id": my_id}

        # client.emit("get_ID", data, callback=set_id_in_config)
        client.emit("get_ID", data)

    @client.event
    def upload_file(self, file_path, file_name):
        """
        Upload video file to the server
        :return:
        """
        name = file_name
        file = open(file_path, "rb")
        video = base64.b64encode(file.read())

        data = {"file": video, "filename": name}
        # data = {"filename": name}

        client.emit("file_upload", data)
    
    @client.event()
    def request_man_open(self, password):
        print(f"testing if the password is passed on {password}")
        data = {"password": password}
        client.emit("man_open_request", data)

    @client.event
    def on_disconnect(self):
        temp_id = self.did
        data = {"id": temp_id}
        client.emit("exit", data=data)
        time.sleep(1)
        client.disconnect()


@client.on("hello")
def get_id(event, data={"None": "None"}):
    """
    This function calls the FileIO to set up the config file on receiving new_id.
    :param
    event:
    data: response received from the server
    """
    print("Received EVENT hello")

    try:
        client.emit("received")
    except:
        print("could not send ack")
    
    try:
        if data is None:
            receiver_thread = threading.Thread(target=response_ids["hello"])
        else:
            receiver_thread = threading.Thread(target=response_ids["hello"](data))

        receiver_thread.start()
        receiver_thread.join()
    except Exception as err:
        print(f"Unexpected error occured {err}")
    
    print("Returned form handling event")


@client.on("set_ID")
def get_id(data):
    """
    This function calls the FileIO to set up the config file on receiving new_id.
    :param
    event:
    data: response received from the server
    """
    print("Received EVENT set_id")

    try:
        client.emit("received")
    except:
        print("could not send ack")

    print(data)

    if data is None:
        receiver_thread = threading.Thread(target=response_ids["hello"])
    else:
        receiver_thread = threading.Thread(target=response_ids["set_ID"](data))

    receiver_thread.start()
    receiver_thread.join()

    print("Returned form handling event")
    
    

@client.on("access_granted")
def get_id(data):
    """
    This function calls the FileIO to set up the config file on receiving new_id.
    :param
    event:
    data: response received from the server
    """
    print("Received EVENT access granted")

    try:
        client.emit("received")
    except:
        print("could not send ack")
    
    print("___________ {data} _________")
    
    try:
        receiver_thread = threading.Thread(target=response_ids["access_granted"](data))

        receiver_thread.start()
        receiver_thread.join()
    except Exception as err:
        print(f"Unexpected error occured {err}")
    
    print("Returned form handling event")
                
    


def open_com_chanel(cl):
    cl.request_id()

