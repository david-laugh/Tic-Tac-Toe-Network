import socket
import select
import pickle


"""
Tic-Tac-Toe Client을 연결하는 서버
"""
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


ROOMS = []
def createRoom(sock):
    # 방을 생성한다.
    ROOMS.append([sock])

def _searchRoom():
    # 한 명의 유저만 있는 방을 탐색한다.
    for i, room in enumerate(ROOMS):
        if len(room) < 2:
            return i
    return ""

def joinRoom(sock):
    # 방에 참가한다.
    try:
        ROOMS[_searchRoom()].append(sock)
        return True
    except TypeError:
        return False


def execute():
    # 1. 소켓을 연결한다.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((IP, PORT))
        s.listen()

        print(f'Listening for connections on {IP}:{PORT}...')

        socket_list = [s]

        # 서버 상태를 유지한다.
        while True:
            read_sockets, _, exception_sockets = \
                select.select(socket_list, [], [])

            # 새로운 소켓을 확인한다.
            for notified_socket in read_sockets:
                if notified_socket == s:
                    new_socket, addr = s.accept()
                    socket_list.append(new_socket)

                    message = receive_message(new_socket)
                    if message == "<CREATE>":
                        send_message(new_socket, "방이 생성되었습니다.")
                        createRoom(new_socket)
                    elif message == "<JOIN>":
                        check = joinRoom(new_socket)
                        if check:
                            send_message(new_socket, "방에 참여하였습니다.")
                        else:
                            send_message(new_socket, "참여 가능한 방이 없습니다.")

                else:
                    message = receive_message(notified_socket, "list")
                    print(message)
                    if message is False:
                        # Remove from list for socket.socket()
                        socket_list.remove(notified_socket)

                        for room in ROOMS:
                            if notified_socket in room:
                                room.remove(notified_socket)
                    if message:
                        for room in ROOMS:
                            if notified_socket in room:
                                print(room)
                                if len(room) > 1:
                                    tmp = room[:]
                                    tmp.remove(notified_socket)
                                    send_message(tmp[0], message, type="list")



if __name__=="__main__":
    execute()
