HEADER = 64
FORMAT = "utf-8"
DISCONNECT_MSG = "OVER N OUT"


def handle_server_messages(conn, addr):
    connected = True
    while connected:

        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MSG:
                connected = False

    conn.close()
