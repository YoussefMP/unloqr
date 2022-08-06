import configparser
import os
from os import path, makedirs
import qrcode


class ConfigManager:

    def __init__(self, d_path):
        self.dir = d_path
        self.c_path = path.join(d_path + "/config.ini")
        self.config = configparser.ConfigParser()

        if not path.exists(self.dir):
            makedirs(self.dir)
        if path.exists(self.c_path):
            self.config.read(self.c_path)

    def initialize_config_file(self, did):
        qr_code = qrcode.make(did)
        qr_path = self.dir + "/ID_Code.png"
        qr_code.save(qr_path)

        self.config["Credentials"] = {"ID": did,
                                      "QR_Code": qr_path
                                      }

        with open(self.c_path, "w", encoding="utf-8") as c_file:
            self.config.write(c_file)

    def get_my_id(self):
        try:
            my_id = self.config.get("Credentials", "id")
            return my_id
        except configparser.NoSectionError:
            return "XXXX"
