from src.environment import TicTacToe


PLAYER_ONE = -1
PLAYER_TWO = 1


def run_client():
    t1 = TicTacToe()
    t1.print_board()
    t1.get_pos(1, 2, PLAYER_ONE)
    t1.print_board()
    t1.get_pos(1, 2, PLAYER_ONE)
    t1.get_pos(2, 1, PLAYER_TWO)
    t1.print_board()


if __name__=="__main__":
    run_client()
