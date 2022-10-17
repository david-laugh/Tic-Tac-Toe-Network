from typing import List
import socket
import errno
import sys
import re
import pickle


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
PLAYER = PLAYER_ONE

BOARD = [[0 for _ in range(5)] for _ in range(5)]
def _player_marks(
        board: List[List[int]], player: int
    ) -> List[int]:
    marks = []
    x = 0
    for rows in board:
        y = 0
        for col in rows:
            if col == player:
                marks.append((x, y))
            y += 1
        x += 1
    return marks

def is_winner(board: List[List[int]], player: int) -> str:
    """
    승리조건 :
        가로는 y만 +1 증가하는 연속적인 4개의 수
        세로는 x만 +1 증가하는 연속적인 4개의 수
        대각선 / 는 x, y가 각각 +1, +1 증가하는 연속적인 4개의 수
        대각선 \ 는 x, y가 각각 +1, -1 증가하는 연속적인 4개의 수
    """
    def _win_conditions(mark):
        common_differences = [(0, 1), (1, 0), (1, 1), (1, -1)]
        return [
            [
                (mark[0] + e[0] * i, mark[1] + e[1] * i) for i in range(4)
            ] for e in common_differences
        ]

    marks = _player_marks(board, player)
    for mark in marks[:-3]:
        for win_condition in _win_conditions(mark):
            if set(set(win_condition) & set(marks)) == set(win_condition):
                print("{} is winner.".format(player))

                return player
    return -1


TOKEN = "<JOIN>"
def execute():
    TURN_TOKEN = 1
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((IP, PORT))

        send_message(s, TOKEN)

        message = receive_message(s)
        print(message)
        if message == "참여 가능한 방이 없습니다.":
            sys.exit()

        while True:
            if TURN_TOKEN == 1:
                message = input("Your Turn : ")

                if re.fullmatch("[0-9], [0-9]", message):
                    x, y = message.split(', ')
                    BOARD[int(y)][int(x)] = PLAYER
                    print(BOARD)
                    send_message(s, BOARD, type="list")
                    TURN_TOKEN *= -1
                    print(TURN_TOKEN)

            elif TURN_TOKEN == -1:
                try:
                    message = receive_message(s, "list")
                    print(message)
                    TURN_TOKEN *= -1

                except IOError as e:
                    if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                        print('Reading error: {}'.format(str(e)))
                        sys.exit()

                except Exception as e:
                    # Any other exception - something happened, exit
                    print('Reading error: '.format(str(e)))
                    sys.exit()


if __name__=="__main__":
    execute()
