from ServerMsgHandler import response_ids
import socketio
import base64
from UnloQR_Client.Client_FileIO import ConfigManager

client = socketio.Client()


class Client:

    def __init__(self):
        self.c_man = ConfigManager("./_Config")
        self.server_url = "https://unloqr.herokuapp.com/"
        # self.server_url = "http://127.0.0.1:5000"

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
    def upload_file(self):
        """
        Upload video file to the server
        :return:
        """
        name = "amv.mp4"
        file = open("./static/AMV.mp4", "rb")
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
    response_ids[event](data)


def open_com_chanel(cl):
    cl.request_id()

    print("Sending upload request")
    # cl.upload_file()
    # print("req sent...")

