import sys
import socket
import errno

from src.environment import TicTacToe
from src.utilities.message import send_message, receive_message


IP = "127.0.0.1"
PORT = 3456
PLAYER_ONE = -1
PLAYER_TWO = 1


def run_client():
    t1 = TicTacToe()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((IP, PORT))

        while True:
            try:
                player, mark_pos = receive_message(sock, "list")

                t1.put_mark(mark_pos[0]. mark_pos[1], player)

                send_message(sock, "list")

            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    print('Reading error: {}'.format(str(e)))
                    sys.exit()

            except Exception as e:
                # Any other exception - something happened, exit
                print('Reading error: '.format(str(e)))
                sys.exit()

    # t1 = TicTacToe()
    # t1.print_board()
    # t1.put_mark(1, 2, PLAYER_ONE)
    # t1.print_board()
    # t1.put_mark(1, 2, PLAYER_ONE)
    # t1.put_mark(2, 1, PLAYER_TWO)
    # t1.print_board()


if __name__=="__main__":
    run_client()
