from typing import List
import socket
import errno
import sys
import re
import pickle


"""
Tic-Tac-Toe Game Room을 참여하는 Client
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

def is_winner(board: List[List[int]], player: int) -> str:
    marks = _player_marks(board, player)

    for mark in marks[:-3]:
        for win_condition in _win_conditions(mark):
            if set(set(win_condition) & set(marks)) == set(win_condition):
                print("{} is winner.".format(player))
                return player

    return 0

def game_draw():
    draw_conditions = []

    for player in [PLAYER_ONE, PLAYER_TWO]:
        tmp_board = []
        for rows in BOARD:
            t = []
            for col in rows:
                if col == player or col == 0:
                    t.append(0)
                else:
                    t.append(col)
            tmp_board.append(t)

        marks = _player_marks(tmp_board, 0)
        for mark in marks[:-3]:
            for win_condition in _win_conditions(mark):
                if set(set(win_condition) & set(marks)) == set(win_condition):
                    draw_conditions.append(False)
                    break

    if draw_conditions[0] == False or draw_conditions[1] == False:
        return False
    else:
        return True

def print_board():
    print("+---+---+---+---+---+")
    for i in range(5):
        for j in range(5):
            if BOARD[i][j] == 1:
                print("| 0", end=" ")
            elif BOARD[i][j] == -1:
                print("| X", end=" ")
            else:
                print("|  ", end=" ")
        print("|")
        print("+---+---+---+---+---+")


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
                draw = game_draw()
                if draw:
                    send_message(s, [], "list")
                    print("무승부입니다.")
                    sys.exit()

                message = input("Your Turn : ")
                if re.fullmatch("[0-9], [0-9]", message):
                    x, y = message.split(', ')
                    BOARD[int(y)][int(x)] = PLAYER
                    print_board()

                    winner = is_winner(BOARD, PLAYER_ONE)
                    if winner == PLAYER_ONE:
                        send_message(s, [], "list")
                        break

                    send_message(s, BOARD, type="list")
                    TURN_TOKEN *= -1

            elif TURN_TOKEN == -1:
                try:
                    draw = game_draw()
                    if draw:
                        print("무승부입니다.")
                        break

                    message = receive_message(s, "list")
                    BOARD[:] = message
                    print_board()
                    winner = is_winner(BOARD, PLAYER_TWO)
                    if winner == PLAYER_TWO:
                        break

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
