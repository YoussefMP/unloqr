from Client_FileIO import ConfigManager

c_man = ConfigManager("./_Config")


def read_msg(response):
    print(response["message"])


def set_id(response):
    print(response)
    response = dict(response)
    new_id = response["idx"]
    c_man.initialize_config_file(new_id)


response_ids = {
    "hello": read_msg,
    "set_ID": set_id
}