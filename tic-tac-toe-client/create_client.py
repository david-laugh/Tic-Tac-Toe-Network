import socket
import errno
import sys
import pickle
import random


IP = "127.0.0.1"
PORT = 3456


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


PLAYER_ONE = -1
PLAYER_TWO = 1
PLAYER = PLAYER_TWO
def select_positions(board):
    positions = []
    for j, rows in enumerate(board):
        for i, col in enumerate(rows):
            if col == 0:
                positions.append((i, j))
    idx = random.randint(0, len(positions))
    return positions[idx]


TOKEN = "<CREATE>"
def execute():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((IP, PORT))

        send_message(s, TOKEN)

        message = receive_message(s)
        print(message)

        while True:
            try:
                message = receive_message(s, "list")
                board = message
                x, y = select_positions(board)
                print((x, y))
                board[y][x] = PLAYER
                send_message(s, board, "list")

            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    print('Reading error: {}'.format(str(e)))
                    sys.exit()

                continue

            except Exception as e:
                # Any other exception - something happened, exit
                print('Reading error: '.format(str(e)))
                sys.exit()


if __name__=="__main__":
    execute()
