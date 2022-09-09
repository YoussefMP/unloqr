import os
import threading
from ServerMsgHandler import response_ids, set_c_man, set_client, check_comms
from socketio.exceptions import ConnectionError
from Client_FileIO import ConfigManager
import socketio
import base64
import time
from flask import jsonify
from threading import Thread
from tkinter import StringVar

try:
    import RPi.GPIO as GPIO
    __raspberry__ = True
    print(f"RPi correctly imported")
except ModuleNotFoundError:
    __raspberry__ = False
    print("problem while importing RPi")

client = socketio.Client(reconnection=True, reconnection_attempts=50)
still_connected = False

server_said_hello = False

class Client:

    break_all = False
    server_ans = ""

    def __init__(self):
        self.c_man = ConfigManager("/home/pi/Desktop/unloqr/UnloQR_Client/_Config")
        self.server_url = "https://unloqr.herokuapp.com/"
        # self.server_url = "http://127.0.0.1:5000"

        set_c_man(self.c_man)
        set_client(self)

    def connect_to_server(self):
        my_id = self.c_man.get_my_id()
        data = {"id": my_id}
        print("Connecting to server...")
        tries = 0
        while tries < 10:
            try:
                tries += 1
                self.server_ans = "Wir Überprüfen die Verbindung"
                client.connect(self.server_url, wait_timeout=5)
                self.server_ans = "Sie Können den QR-Code scannen"
                print("_______________EXception?__________")
                break
                print("ZES SIRR")
            except ConnectionError as err:
                if "Already" in str(err):
                    self.server_ans = "Nicht mehr mit Server verbunden..."
                    print("Already Connected")
                    if tries < 3:
                        print("Client Disconnected")
                        client.disconnect()
                        time.sleep(1)
                    elif tries > 3:                        
                        break
                print(f"Caught Connection Error {tries}, retrying... ")
                time.sleep(1)
            except Exception:
                self.server_ans = "Nicht mehr mit Server verbunden..."
                time.sleep(1)

        client.emit("connected?", data)
        print("finished the connection loop")

    @client.event
    def request_id(self):
        """
        On app's first start this method will request ID for device from server
        :return: True, if server accepted request and sends ID back
        """
        my_id = self.c_man.get_my_id()
        data = {"id": my_id}
        
        def rerequest_id(cl):
            global server_said_hello 
            time.sleep(3)
            tries = 0
            while not server_said_hello:
                tries += 1
                print("Hey SERVER!...")
                client.emit("get_ID", data)
                time.sleep(5)
                if tries % 3 == 0:
                    cl.connect_to_server()
                elif tries == 4:
                    from tkinter.messagebox import showerror as ShowError
                    ShowError(title="Crash", message="Server antwortet nicht, bitte neu starten")
                    time.sleep(2)
                    psutil.Process(os.getpid()).terminate()
                
        client.emit("get_ID", data)
        re_request_thread = Thread(target=lambda: rerequest_id(self))
        re_request_thread.start()
        re_request_thread.join()
        
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
        print("Finished Uploading file")
    
    @client.event()
    def request_man_open(self, password):
        print(f"testing if the password is passed on {password}")
        data = {"password": password}
        client.emit("man_open_request", data)
        
    @client.event()
    def request_close_app(self, password):
        data = {"password": password}
        client.emit("close_app", data)

    @client.event()
    def check_connection(self,):
        my_id = self.c_man.get_my_id()
        data = {"id": my_id}
        print("Am i still connected?")
        client.emit("connected?", data)
        
        def reconnect():
            global still_connected
            
            time.sleep(3)
            print(still_connected)
            if not still_connected:
                self.connect_to_server()
            
            still_connected = False
        
        reconnect_thread = Thread(target=reconnect)
        reconnect_thread.start()
        reconnect_thread.join()
            
    @client.event()
    def on_disconnect(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(13, GPIO.OUT)
        GPIO.output(13, 0)
        temp_id = self.did
        data = {"id": temp_id}
        client.emit("exit", data=data)
        time.sleep(1)
        client.disconnect()


@client.on("yes")
def server_says_yes():
    global still_connected
    still_connected = True
    print("server says yes")
    Client.server_ans = "Verbindung hergestellt"
    
    
@client.on("hello")
def get_id(event, data={"None": "None"}):
    """
    This function calls the FileIO to set up the config file on receiving new_id.
    :param
    event:
    data: response received from the server
    """
    print("Received EVENT hello")
    Client.server_ans = "Server sagt Hallo"
    global server_said_hello
    server_said_hello = True
    
    try:
        client.emit("received")
    except:
        print("could not send ack")
    finally:
        check_comms()
    
    
    try:
        if data is None:
            receiver_thread = threading.Thread(target=response_ids["hello"])
        else:
            receiver_thread = threading.Thread(target=response_ids["hello"](data))

        receiver_thread.start()
        receiver_thread.join()
    finally:
        check_comms()
    
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
    global server_said_hello
    server_said_hello = True

    try:
        client.emit("received")
    except:
        print("could not send ack")

    print(data)
    try:
        if data is None:
            receiver_thread = threading.Thread(target=response_ids["hello"])
        else:
            receiver_thread = threading.Thread(target=response_ids["set_ID"](data))

        receiver_thread.start()
        receiver_thread.join()
    except Exception as err:
        print(f"Error handling set id {err}")
    finally:
        check_comms()
    print("Returned form handling event")
    

@client.on("access_granted")
def grant_access(data):
    """
    This function calls the FileIO to set up the config file on receiving new_id.
    :param
    event:
    data: response received from the server
    """
    print("Received EVENT access granted")
    Client.server_ans = "Server sagt du darfst durch"
    try:
        print("\t sending acknowlegment")
        client.emit("received")
    except:
        print("could not send ack")
    finally:
        print("\t checking comms after ack")
        check_comms()
        
    try:
        print("starting acces grantion thread")
        receiver_thread = threading.Thread(target=response_ids["access_granted"](data))

        receiver_thread.start()
        print("waiting on thread to finish")
        receiver_thread.join()
        print("Print done waiting for user to go in")
    except Exception as err:
        print(f"Unexpected error occured {err}")
    finally:
        print("checking connection after thread of access granted finished")
        check_comms()
    
    print("Returned form handling event")
                

@client.on("file_got")
def delete_file(data):
    print("Deleting video from local folder")
    from pathlib import Path
    try:
        [f.unlink() for f in Path("./static/uploads/").glob("*") if f.is_file()]
    finally:
        check_comms()
    
@client.on("close_ok")
def close_ok():
    
    Client.break_all = True
    


def open_com_chanel(cl):
    cl.request_id()

