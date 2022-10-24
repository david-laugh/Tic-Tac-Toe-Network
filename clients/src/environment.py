from typing import List


PLAYER_ONE = -1
PLAYER_TWO = 1


class TicTacToe:
    def __init__(self) -> None:
        self.board = self._board()

    def _board(self) -> List[List[int]]:
        return [[0 for _ in range(5)] for _ in range(5)]

    def print_board(self) -> None:
        print("+---+---+---+---+---+")
        for row in self.board:
            for col in row:
                if col == PLAYER_ONE:
                    print("| X ", end="")
                elif col == PLAYER_TWO:
                    print("| O ", end="")
                else:
                    print("|   ", end="")
            print("|")
            print("+---+---+---+---+---+")

    def put_mark(self, col: int, row: int, player: int) -> None:
        if self.board[row][col] == 0:
            self.board[row][col] = player
        else:
            print("빈 칸이 아닙니다.")

    def _get_mark_list(self, player: int) -> None:
        mark_list = []
        for i, row in enumerate(self.board):
            for j, col in enumerate(row):
                if col == player:
                    mark_list.append((j, i)) 
        return mark_list

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

    def win(self, player: int) -> None:
        mark_list = self._get_markList(player)

        for mark in mark_list[:-3]:
            for win_condition in self._win_conditions(mark):
                if set(set(win_condition) & set(mark_list)) == set(win_condition):
                    print("{} is winner.".format(player))
                    return player

        return 0

    def draw(self) -> bool:
        mark_list_one = self._get_markList(PLAYER_ONE) + self._get_markList(0)
        mark_list_two = self._get_markList(PLAYER_TWO) + self._get_markList(0)
        s1, s2 = False, False

        for mark_one, mark_two in zip(mark_list_one[:-3], mark_list_two[:-3]):
            for win_condition_one, win_condition_two \
                in zip(self._win_conditions(mark_one), self._win_conditions(mark_two)):
                if set(set(win_condition_one) & set(mark_list_one)) == set(win_condition_one):
                    s1 = True
                    # break 제어 추가...
                if set(set(win_condition_two) & set(mark_list_two)) == set(win_condition_two):
                    s2 = True

        # 둘 다 False일 경우에 draw
        if s1 == True or s2 == True:
            return False
        else:
            return True
