
import select
import socket
import random


IP = "127.0.0.1"
PORT = 3456

ROOMS = []
MAX_ROOM_SIZE = 2
MIN_ROOM_SIZE = 2


def _searchRoom():
    # 한 명의 유저만 있는 방을 탐색한다.
    for i, room in enumerate(ROOMS):
        if len(room) < 2:
            return i
    return ""

def createRoom(sock):
    # 방을 생성한다.
    ROOMS.append([sock])

def _searchRoom():
    # 한 명의 유저만 있는 방을 탐색한다.
    for i, room in enumerate(ROOMS):
        if len(room) < 2:
            return i
    return ""

def run():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((IP, PORT))
        sock.listen()

        print(f'Listening for connections on {IP}:{PORT}...')

        socket_list = [sock]

        while True:
            read_sockets, _, _ = \
                select.select(socket_list, [], [])

            for notified_socket in read_sockets:
                if notified_socket == sock:
                    new_sock, addr = sock.accept()
                    socket_list.append(new_sock)
                    print(socket_list)

                    # 방이 없다면,
                    for room in ROOMS:
                        if len(room) > 1:
                            ROOMS.append([socket_list])
                            createRoom(new_socket)
                        else:
                            room

            # random token
            # r = random.choice([-1, 1])
            # print(r)
            # pass


if __name__=="__main__":
    run()
