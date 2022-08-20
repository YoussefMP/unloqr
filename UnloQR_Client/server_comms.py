import threading
from ServerMsgHandler import response_ids, set_c_man, set_client
from Client_FileIO import ConfigManager
import socketio
import base64


client = socketio.Client()


class Client:

    def __init__(self):
        self.c_man = ConfigManager("./_Config")
        # self.server_url = "https://unloqr.herokuapp.com/"
        self.server_url = "http://127.0.0.1:5000"

        set_c_man(self.c_man)
        set_client(self)

        print("Connecting to server...")
        client.connect(self.server_url, wait_timeout=10)

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
        name = file_path[file_path.rfind("/")+1:]
        file = open(file_path, "rb")
        video = base64.b64encode(file.read())

        data = {"file": video, "filename": name}
        # data = {"filename": name}

        client.emit("file_upload", data)


@client.on("*")
def get_id(event, data):
    """
    This function calls the FileIO to set up the config file on receiving new_id.
    :param
    event:
    data: response received from the server
    """
    print("Received EVENT")
    receiver_thread = threading.Thread(target=response_ids[event](data))
    receiver_thread.start()


def open_com_chanel(cl):
    cl.request_id()

