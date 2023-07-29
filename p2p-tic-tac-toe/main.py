import socket
import struct
import argparse

PORT = 22301
# you may need to tweak this, for example if u want to deploy this to a VPS and test it, a get request to whatismyip might work
IP = socket.gethostbyname(socket.gethostname())

class Player:
    def get_player_move(self):
        return input("Choose your move:\n1, 2, 3\n4, 5, 6\n7, 8, 9\n")

    def validate_input(self, value: str, board):
        try:
            value = int(value)
        except ValueError:
            return False
        
        
        if not 1 <= value <= 9:
            return False

        return not board[(value - 1) // 3][(value - 1) % 3]


class ListeningPeer(Player):
    def __init__(self):
        self.symbol = "X"

    def initialize(self):
        print("Waiting for opponent\n")

        print(socket.gethostbyaddr(socket.gethostname())[2][0])
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((IP, PORT))

        sock.listen(3)

        while True:
            conn, address = sock.accept()

            print(f"Connected to {address}")

            if self.handshake(conn):
                self.conn = conn
                print("Handshake complete\n")
                break
            else:
                print("Failed Handshake\n")
                conn.close()

    
    def handshake(self, conn):
        resp = conn.recv(1)
        resp = struct.unpack("B", resp)[0]

        if resp != 69:
            return False

        conn.send(struct.pack("B", 69))

        ack = conn.recv(1)
        ack = struct.unpack("B", ack)[0]

        return ack == 1

    def do_move(self, move):
        self.conn.send(struct.pack("B", move))

    def wait_opponent_move(self):
        move = self.conn.recv(1)
        return struct.unpack("B", move)[0]


class ConnectingPeer(Player):
    def __init__(self, target_ip: str):
        self.symbol = "O"
        self.target_ip = target_ip 


    def initialize(self):
        print(f"Connecting to opponent {self.target_ip}")

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.connect((self.target_ip, PORT))

        if self.handshake(sock):
            self.conn = sock
            print("Handshake complete\n")
        else:
            print("Failed Handshake\n")
            sock.close()


    def handshake(self, sock):
        sock.send(struct.pack("B", 69))
        response = sock.recv(1)

        resp = struct.unpack("B", response)[0]

        if resp != 69:
            return False
        
        sock.send(struct.pack("B", 1))

        return True
    
    def do_move(self, move):
        self.conn.send(struct.pack("B", move))

    def wait_opponent_move(self):
        move = self.conn.recv(1)
        return struct.unpack("B", move)[0]


class Game:
    def __init__(self, player: Player):
        self.board = [[None for i in range(3)] for _ in range(3)]
        self.is_over = False
        self.player = player
        self.winning = False
        self.play_count = 0
    
    def run(self):
        if self.player.symbol == "X":
            self.run_listening_peer()
        else:
            self.run_connecting_peer()

    def run_listening_peer(self):
        """ Listening peer begins playing """
        while True:
            print(self)
            while True:
                player_move = player.get_player_move()
                if player.validate_input(player_move, self.board):
                    break
                print("Invalid option!\n")

            self.player.do_move(int(player_move))
            self.update_board(int(player_move), self.player.symbol)

            if self.is_over:
                break

            print(self)
            print("Waiting on opponent to move\n")
            opponent_move = player.wait_opponent_move()
            self.update_board(int(opponent_move), "O")
            
            if self.is_over:
                break
        
        print("Game Over!")
        print(self)

    def run_connecting_peer(self):
        while True:
            print(self)
            print("Waiting on opponent to move\n")
            opponent_move = player.wait_opponent_move()
            self.update_board(int(opponent_move), "X")

            if self.is_over:
                break

            print(self)
            while True:
                player_move = player.get_player_move()
                if player.validate_input(player_move, self.board):
                    break
                print("Invalid option!\n")
            
            self.player.do_move(int(player_move))
            self.update_board(int(player_move), self.player.symbol)

            if self.is_over:
                break
        
        print("Game Over!")
        print(self)

    def update_board(self, move: int, symbol: str):
        line = (move - 1) // 3
        col = (move - 1) % 3
        self.board[line][col] = symbol
        self.play_count += 1

        self.check_over(symbol)
   
    def check_over(self, symbol):
        if self.play_count == 9:
            self.is_over = True

        # check lines
        if all(x == symbol for x in self.board[0]):
            self.is_over = True
        if all(x == symbol for x in self.board[1]):
            self.is_over = True
        if all(x == symbol for x in self.board[2]):
            self.is_over = True

        # check columns
        if self.board[0][0] == self.board[1][0] == self.board[2][0] == symbol:
            self.is_over = True
        if self.board[0][1] == self.board[1][1] == self.board[2][1] == symbol:
            self.is_over = True
        if self.board[0][2] == self.board[1][2] == self.board[2][2] == symbol:
            self.is_over = True
        
        # check diagonals
        if self.board[0][0] == self.board[1][1] == self.board[2][2] == symbol:
            self.is_over = True
        if self.board[0][2] == self.board[1][1] == self.board[2][0] == symbol:
            self.is_over = True
 

    def __str__(self):
        board_str = "-" * 13 + "\n"
        for line in self.board:
            board_str += "|"
            for value in line:
                board_str += " "
                board_str += value if value else " "
                board_str += " "
                board_str += "|"
            board_str += "\n"
            board_str += "-" * 13 + "\n"
        
        return board_str


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Tic Tac Toe", description="A p2p tic tac toe")

    parser.add_argument("-i", "--ip", metavar="", help="opponent's IP address")

    args = parser.parse_args()

    if args.ip:
        player = ConnectingPeer(args.ip)
    else:
        player = ListeningPeer()
    
    player.initialize()
    
    game = Game(player)
    game.run()
