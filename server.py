from typing import List
import socket
import select
import re
import pickle

HEADER_LENGTH = 10

IP = "127.0.0.1" #Local(Internal) IP 주소 지정
PORT = 1234 #Port 번호 지정 (충돌시 변경가능)

PLAYER_ONE = 1
PLAYER_TWO = 2
WIN_PLAYER = -1

class TicTacToe:
    def __init__(self) -> None:
        self.board = [[0 for _ in range(5)] for _ in range(5)]

    def _player_marks(
            self, board: List[List[int]], player: int
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

    def is_winner(self, board: List[List[int]], player: int) -> str:
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

        marks = self._player_marks(board, player)
        for mark in marks[:-3]:
            for win_condition in _win_conditions(mark):
                if set(set(win_condition) & set(marks)) == set(win_condition):
                    print("{} is winner.".format(player))

                    return player
        return -1

SOCKETS = {}
GAMEROOMS = []
_id = 0

# 소켓을 생성한다.
# socket.AF_INET - address family, IPv4, some otehr possible are AF_INET6, AF_BLUETOOTH, AF_UNIX
# socket.SOCK_STREAM - TCP, conection-based, socket.SOCK_DGRAM - UDP, connectionless, datagrams, socket.SOCK_RAW - raw IP packets
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# SO_ - socket option
# SOL_ - socket option level
# Sets REUSEADDR (as a socket option) to 1 on socket
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind, so server informs operating system that it's going to use given IP and port
# For a server using 0.0.0.0 means to listen on all available interfaces, useful to connect locally to 127.0.0.1 and remotely to LAN interface IP
server_socket.bind((IP, PORT))

# This makes server listen to new connections
server_socket.listen()

# List of sockets for select.select()
sockets_list = [server_socket]

# List of connected clients - socket as a key, user header and name as data
clients = {}

print(f'Listening for connections on {IP}:{PORT}...')

# Handles message receiving
def receive_message(client_socket):
    try:
        # Receive our "header" containing message length, it's size is defined and constant
        message_header = client_socket.recv(HEADER_LENGTH)

        # If we received no data, client gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
        if not len(message_header):
            return False

        # Convert header to int value
        message_length = int(message_header.decode('utf-8').strip())

        # Return an object of message header and message data
        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:
        # If we are here, client closed connection violently, for example by pressing ctrl+c on his script
        # or just lost his connection
        # socket.close() also invokes socket.shutdown(socket.SHUT_RDWR) what sends information about closing the socket (shutdown read/write)
        # and that's also a cause when we receive an empty message
        return False

while True:
    # Calls Unix select() system call or Windows select() WinSock call with three parameters:
    #   - rlist - sockets to be monitored for incoming data
    #   - wlist - sockets for data to be send to (checks if for example buffers are not full and socket is ready to send some data)
    #   - xlist - sockets to be monitored for exceptions (we want to monitor all sockets for errors, so we can use rlist)
    # Returns lists:
    #   - reading - sockets we received some data on (that way we don't have to check sockets manually)
    #   - writing - sockets ready for data to be send thru them
    #   - errors  - sockets with some exceptions
    # This is a blocking call, code execution will "wait" here and "get" notified in case any action should be taken
    read_sockets, _, exception_sockets = \
        select.select(sockets_list, [], sockets_list)

    # Iterate over notified sockets
    for notified_socket in read_sockets:
        # If notified socket is a server socket - new connection, accept it
        if notified_socket == server_socket:
            # Accept new connection
            # That gives us new socket - client socket, connected to this given client only, it's unique for that client
            # The other returned object is ip/port set
            client_socket, client_address = server_socket.accept()

            # Client should send his name right away, receive it
            user = receive_message(client_socket)

            # If False - client disconnected before he sent his name
            if user is False:
                continue

            # Add accepted socket to select.select() list
            sockets_list.append(client_socket)

            # Also save username and username header
            clients[client_socket] = user

            print(
                'Accepted new connection from {}:{}, username: {}' \
                    .format(*client_address, user['data'].decode('utf-8'))
            )
            SOCKETS[user['data'].decode('utf-8').split(" ")[-1]] = client_address

            print("Create GAME ROOM : {}".format(user['data'].decode('utf-8')))
            # 게임방을 생성하는 플레이어는 Player One
            if "Create a Game Room" in user['data'].decode('utf-8'):
                tmp = user['data'].decode('utf-8')
                hostName = tmp.split(" ")[-1]
                GAMEROOMS.append(
                    {
                        "_id": _id,
                        "HOST NAME": hostName,
                        "Board" : TicTacToe().board,
                        "YOUR TURN" : PLAYER_ONE,
                        "Player" : {
                            "PLAYER_ONE" : hostName,
                            "PLAYER_TWO" : ""
                        }
                    }
                )
            # 게임방을 참가하는 플레이어는 Player Two
            elif "Join the Game Room" in user['data'].decode('utf-8'):
                tmp = user['data'].decode('utf-8')
                hostName, user = tmp.split(" ")[-2], tmp.split(" ")[-1]
                gameRoom = next((item for item in GAMEROOMS if item["HOST NAME"] == hostName), None)
                gameRoom["Player"]["PLAYER_TWO"] = user

            # 다음 생성된 방 id는 1씩 증가.
            _id += 1

        # Else existing socket is sending a message
        else:
            # Receive message
            message = receive_message(notified_socket)

            # If False, client disconnected, cleanup
            if message is False:
                print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))

                # Remove from list for socket.socket()
                sockets_list.remove(notified_socket)

                # Remove from our list of users
                del clients[notified_socket]

                continue

            # Get user by notified socket, so we will know who sent the message
            user = clients[notified_socket]

            print(
                f'Received message from \
                    {user["data"].decode("utf-8").split(" ")[-1]}: \
                    {message["data"].decode("utf-8")}'
            )

            # 해당 message가 좌표값인지
            if re.fullmatch("[0-9], [0-9]", message["data"].decode("utf-8")):
                x, y = message["data"].decode("utf-8").split(', ')
                tmp = user['data'].decode('utf-8')
                playerName = tmp.split(" ")[-1]

                gameRoom = next((item for item in GAMEROOMS if playerName in item["Player"].values()), None)

                if ( dict(map(reversed, gameRoom["Player"].items()))[playerName] == "PLAYER_ONE" \
                    and gameRoom["YOUR TURN"] == PLAYER_ONE ) \
                    or ( dict(map(reversed, gameRoom["Player"].items()))[playerName] == "PLAYER_TWO" \
                    and gameRoom["YOUR TURN"] == PLAYER_TWO ):
                        gameRoom["Board"][int(y)][int(x)] = gameRoom["YOUR TURN"]

                        if gameRoom["YOUR TURN"] == PLAYER_ONE:
                            WIN_PLAYER = TicTacToe().is_winner(gameRoom["Board"], gameRoom["YOUR TURN"])
                            gameRoom["YOUR TURN"] = PLAYER_TWO
                        else:
                            WIN_PLAYER = TicTacToe().is_winner(gameRoom["Board"], gameRoom["YOUR TURN"])
                            gameRoom["YOUR TURN"] = PLAYER_ONE
                else:
                    print("해당 유저의 턴이 아닙니다.")

            # Iterate over connected clients and broadcast message
            for client_socket in clients:
                # But don't sent it to sender
                if client_socket != notified_socket:
                    # Send user and message (both with their headers)
                    # We are reusing here message header sent by sender, and saved username header send by user when he connected
                    tmp = user['data'].decode('utf-8')
                    playerName = tmp.split(" ")[-1]

                    gameRoom = next((item for item in GAMEROOMS if playerName in item["Player"].values()), None)

                    board = gameRoom["Board"]
                    board = pickle.dumps(board)
                    board_header = f"{len(board):<{HEADER_LENGTH}}".encode('utf-8')

                    if WIN_PLAYER > 0:
                        players = list(gameRoom["Player"].values())
                        players = "_".join(players)

                        player = players.encode('utf-8')
                        player_header = f"{len(player):<{HEADER_LENGTH}}".encode('utf-8')

                        message = f"{playerName} is winner.".encode('utf-8')
                        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
                        client_socket.send(
                            user['header'] + user['data']
                            + message_header + message
                            + player_header + player
                            + board_header + board
                        )
                        notified_socket.send(
                            user['header'] + user['data']
                            + message_header + message
                            + player_header + player
                            + board_header + board
                        )
                    else:
                        players = list(gameRoom["Player"].values())
                        players.remove(playerName)

                        player = players[0].encode('utf-8')
                        player_header = f"{len(player):<{HEADER_LENGTH}}".encode('utf-8')

                        client_socket.send(
                            user['header'] + user['data']
                            + message['header'] + message['data']
                            + player_header + player
                            + board_header + board
                        )

    # It's not really necessary to have this, but will handle some socket exceptions just in case
    for notified_socket in exception_sockets:

        # Remove from list for socket.socket()
        sockets_list.remove(notified_socket)

        # Remove from our list of users
        del clients[notified_socket]
