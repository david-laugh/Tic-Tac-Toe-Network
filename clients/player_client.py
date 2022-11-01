import sys
import socket
import errno

from src.utilities.message import send_message, receive_message


IP = "127.0.0.1"
PORT = 3456


def execute():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((IP, PORT))

        # send_message(s, "Hello")

        while True:
            try:
                turn, board, message = receive_message(sock, "list")

                if turn:
                    message = input("My Turn : ")
                    send_message(sock, message)

            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    print('Reading error: {}'.format(str(e)))
                    sys.exit()

            except Exception as e:
                # Any other exception - something happened, exit
                print('Reading error: '.format(str(e)))
                sys.exit()


if __name__ == "__main__":
    execute()
