import socket
import errno
import sys
import pickle

import pygame


HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1234

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

HEIGHT = 600
WIDTH = 600

CELL_SIZE = 120

PLAYER_ONE = 1
PLAYER_TWO = 2


class Cell:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y
        self.symbol = 0

    def __str__(self):
        return str(self.symbol)

    def __repr__(self):
        return str(self.symbol) + str([str(self.x), str(self.y)])

    def mark(self, symbol):
        # mark the cell with the correct symbol for the player
        # after this we check for win conditions
        self.symbol = symbol

    def draw(self, screen):
        rectangle = pygame.Rect(self.x, self.y, CELL_SIZE, CELL_SIZE)
        # draw the rectangle. Have to draw 2 rects to get a stroke :(
        pygame.draw.rect(screen, BLACK, rectangle, 1)
        if self.symbol == PLAYER_ONE:
            text = "X"
        elif self.symbol == PLAYER_TWO:
            text = "O"
        else:
            text = " "

        label = largeFont.render(text, 1, BLACK)
        text_x = self.x - (label.get_rect().width / 2) + (CELL_SIZE / 2)
        text_y = self.y - (label.get_rect().height / 2) + (CELL_SIZE / 2)
        screen.blit(largeFont.render(text, 1, BLACK), (text_x, text_y))


def board_filled(board):
    """
    Checks if the board is all filled
    :param board: 
    :return: 
    """
    for row in board:
        for cell in row:
            if cell.symbol == 0:
                return False
    return True

def build_board():
    board = []
    for i in range(0, 5):
        row = []
        for j in range(0, 5):
            cell_x = (j * CELL_SIZE)
            cell_y = (i * CELL_SIZE)
            row.append(Cell(cell_x, cell_y))
        board.append(row)
    return board

BOARD = [[0 for _ in range(5)] for _ in range(5)]
def draw_board(game_board, board):
    screen.fill(WHITE)
    for g_rows, b_rows in zip(game_board, board):
        for g_cell, b_cell in zip(g_rows, b_rows):
            if g_cell.symbol == 0 and b_cell != 0:
                g_cell.mark(b_cell)
                g_cell.draw(screen)
            elif g_cell.symbol != 0:
                g_cell.draw(screen)
            else:
                g_cell.draw(screen)


game_over = False

command = input("Command: ")
if "Create a Game Room" in command:
    current_player = PLAYER_ONE
    MY_TURN = 1
elif "Join the Game Room":
    current_player = PLAYER_TWO
    MY_TURN = -1

my_username = command.split(" ")[-1]

# 소켓을 생성
# socket.AF_INET - address family, IPv4, some otehr possible are AF_INET6, AF_BLUETOOTH, AF_UNIX
# socket.SOCK_STREAM - TCP, conection-based, socket.SOCK_DGRAM - UDP, connectionless, datagrams, socket.SOCK_RAW - raw IP packets
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to a given ip and port
client_socket.connect((IP, PORT))

# Set connection to non-blocking state, so .recv() call won;t block, just return some exception we'll handle
client_socket.setblocking(False)

# Prepare username and header and send them
# We need to encode username to bytes, then count number of bytes and prepare header of fixed size, that we encode to bytes as well
command = command.encode('utf-8')
command_header = f"{len(command):<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(command_header + command)

START = True
while True:
    if "Computer" in my_username:
        # Wait for user to input a message
        message = input(f'{my_username} > ')

        # If message is not empty - send it
        if message:
            # Encode message to bytes, prepare header and convert to bytes, like for username above, then send
            message = message.encode('utf-8')
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
            client_socket.send(message_header + message)

    else:
        if START:
            pygame.init()

            GAME_NAME = f"Tic-Tac-Toe - {my_username}"

            screen = pygame.display.set_mode((HEIGHT, WIDTH))

            pygame.display.set_caption(GAME_NAME)
            screen.fill(WHITE)

            largeFont = pygame.font.SysFont("monospace", 60)
            smallFont = pygame.font.SysFont("monospace", 30)

            game_board = build_board()

            START = False

        if MY_TURN == 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                    # mark the appropriate cell
                    # get the position of the mouse
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    # check each cell to see if it's in that cell
                    for row in game_board:
                        for cell in row:
                            if mouse_x >= cell.x and mouse_x <= cell.x + CELL_SIZE:
                                if mouse_y >= cell.y and mouse_y <= cell.y + CELL_SIZE:
                                    if cell.symbol == 0:
                                        # its in this cell, so we can mark it with the current player's symbol
                                        cell.mark(current_player)
                                        x = int(cell.x / CELL_SIZE)
                                        y = int(cell.y / CELL_SIZE)

                                        message = f"{x}, {y}".encode('utf-8')
                                        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
                                        client_socket.send(message_header + message)

                                        BOARD[y][x] = current_player
                    MY_TURN *= -1

        screen.fill(WHITE)

        draw_board(game_board, BOARD)

        pygame.display.update()

    try:
        # Now we want to loop over received messages (there might be more than one) and print them
        while True:

            # Receive our "header" containing username length, it's size is defined and constant
            command_header = client_socket.recv(HEADER_LENGTH)

            # If we received no data, server gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
            if not len(command_header):
                print('Connection closed by the server')
                sys.exit()

            # Convert header to int value
            username_length = int(command_header.decode('utf-8').strip())

            # Receive and decode username
            username = client_socket.recv(username_length).decode('utf-8')
            username = username.split(" ")[-1]

            # Now do the same for message (as we received username, we received whole message, there's no need to check if it has any length)
            message_header = client_socket.recv(HEADER_LENGTH)
            message_length = int(message_header.decode('utf-8').strip())
            message = client_socket.recv(message_length).decode('utf-8')

            player_header = client_socket.recv(HEADER_LENGTH)
            player_length = int(player_header.decode('utf-8').strip())
            player = client_socket.recv(player_length).decode('utf-8')

            if my_username in player:
                board_header = client_socket.recv(HEADER_LENGTH)
                board_length = int(board_header.decode('utf-8').strip())
                board = client_socket.recv(board_length)
                BOARD = pickle.loads(board)

                print(f'{username} > {message}')
                if " is winner." in message:
                    print(message)
                    sys.exit()

                MY_TURN *= -1

            else:
                board_header = client_socket.recv(HEADER_LENGTH)
                board_length = int(board_header.decode('utf-8').strip())
                board = client_socket.recv(board_length)
                _ = pickle.loads(board)


    except IOError as e:
        # This is normal on non blocking connections - when there are no incoming data error is going to be raised
        # Some operating systems will indicate that using AGAIN, and some using WOULDBLOCK error code
        # We are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
        # If we got different error code - something happened
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error: {}'.format(str(e)))
            sys.exit()

        # We just did not receive anything
        continue

    except Exception as e:
        # Any other exception - something happened, exit
        print('Reading error: '.format(str(e)))
        sys.exit()
