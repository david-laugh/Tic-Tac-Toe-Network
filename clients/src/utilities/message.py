import pickle


HEADER_LENGTH = 10


def send_message(sock, message, type="str"):
    if type == "str":
        message = message.encode('utf-8')
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
        sock.send(message_header + message)
    else:
        message = pickle.dumps(message)
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
        sock.send(message_header + message)


def receive_message(client_socket, type="str"):
    if type == "str":
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
        message_length = int(message_header.decode('utf-8').strip())
        message = client_socket.recv(message_length)
        return message.decode('utf-8')
    else:
        board_header = client_socket.recv(HEADER_LENGTH)
        board_length = int(board_header.decode('utf-8').strip())
        board = client_socket.recv(board_length)
        BOARD = pickle.loads(board)
        return BOARD
