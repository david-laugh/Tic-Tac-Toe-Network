# Tic-Tac-Toe-Network
Socket 통신을 활용한 Tic-Tac-Toe 게임

## Example
1. 총 세개의 터미널을 준비해주세요. 각각 해당 Command로 실행합니다.  
    ```
    python server.py
    ```  
    ```
    python client.py
    Create a Game Room User1
    ```  
    ```
    python client.py
    Join the Game Room User1 User2
    ```  
2. 실행된 Pygame 보드에서 TicTacToe을 플레이합니다.
    + 방을 만든 유저가 선 플레이어입니다.

## Command Explanation
```
Create a Game Room User1
Create a Game Room [ 플레이어 이름이면서 방 이름 ]
```
```
Join the Game Room User1 User2
Join the Game Room [ 방 이름 ] [ 플레이어 이름 ]
```
* 플레이어 이름에 `Computer`을 포함하면 Pygame보드가 나타나지 않고, 터미널에서 게임을 진행하게 됩니다.
