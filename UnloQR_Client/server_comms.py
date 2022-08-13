from Client_FileIO import ConfigManager
import socketio
import base64


client = socketio.Client()


class Client:

    def __init__(self):
        self.c_man = ConfigManager("./_Config")
        self.server_url = "https://unloqr.herokuapp.com"

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

        def set_id_in_config(idx):
            """
            This function calls the FileIO to set up the config file on receiving new_id.
            :param idx: New ID received from the server or None
            """
            if idx != "XXXX":
                self.c_man.initialize_config_file(idx)

        client.emit("get_ID", data, callback=set_id_in_config)

    @client.event
    def upload_file(self):
        """
        Upload video file to the server
        :return:
        """
        name = "amv.mp4"
        file = open("./static/AOT.mp4", "rb")
        video = base64.b64encode(file.read())

        data = {"file": video, "filename": name}
        # data = {"filename": name}

        client.emit("file_upload", data)


def open_com_chanel(cl):
    cl.request_id()

    print("Sending upload request")
    cl.upload_file()
    print("req sent...")
    client.disconnect()


