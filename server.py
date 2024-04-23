import threading
import random
import time
import pickle
import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
address = input("server ip (hostname -I) : ")
server_socket.bind((address, 5050))
server_socket.listen(5)


class Game:
    def __init__(self, rows, cols, client_socket, addr):
        self.stop = False
        self.addr = addr
        self.client_socket = client_socket
        self.rows = rows
        self.cols = cols
        self.exitX = 0
        self.exitY = 0
        self.playerX = 0
        self.playerY = 0
        self.monsterX = 0
        self.monsterY = 0
        self.matrix = [['' for _ in range(self.cols)]
                       for _ in range(self.rows)]
        random_number = random.randint(1, 5)
        path = "map"+str(random_number)+".txt"
        with open(path, 'r') as file:
            for row_index in range(self.rows):
                line = file.readline().strip()
                for col_index in range(self.cols):
                    if line[col_index] == "E":
                        self.exitX = row_index
                        self.exitY = col_index
                        self.matrix[row_index][col_index] = " "
                    elif line[col_index] == "H":
                        self.playerX = row_index
                        self.playerY = col_index
                        self.matrix[row_index][col_index] = "."
                    elif line[col_index] == "M":
                        self.monsterX = row_index
                        self.monsterY = col_index
                        self.matrix[row_index][col_index] = "."
                    else:
                        self.matrix[row_index][col_index] = line[col_index]

    def caught(self):
        check = self.playerX == self.monsterX and self.playerY == self.monsterY
        if check:
            self.stop = True
            game_state = {
                'status': 'end',
                'message': 'Ai picat pradă monstrului din labirint 🙁… ai pierdut jocul. Încerca din nou!'
            }
            object_copy = pickle.dumps(game_state)
            self.client_socket.send(object_copy)
        return check

    def exit(self):
        check = self.playerX == self.exitX and self.playerY == self.exitY
        if check:
            self.stop = True
            game_state = {
                'status': 'end',
                'message': 'Ai iesit !'
            }
            object_copy = pickle.dumps(game_state)
            self.client_socket.send(object_copy)
        return check

    def check_obstacle(self, x, y):
        return self.matrix[x][y] != '#'

    def preventEscape(self, x, y):
        return x == self.exitX and y == self.exitY

    def monster_movement(self):
        while self.stop != True:
            game_state = {
                'playerX': self.playerX,
                'playerY': self.playerY,
                'monsterX': self.monsterX,
                'monsterY': self.monsterY,
                'rows': self.rows,
                'cols': self.cols,
                'matrix': self.matrix,
            }
            object_copy = pickle.dumps(game_state)
            self.client_socket.send(object_copy)
            if (self.caught()):
                break
            if self.exit():
                break
            random_move = random.choice(['w', 'a', 'd', 's'])
            if random_move == 'w':
                if self.check_obstacle(self.monsterX - 1, self.monsterY) and self.preventEscape(self.monsterX - 1, self.monsterY) == False:
                    self.monsterX -= 1
            elif random_move == 'a':
                if self.check_obstacle(self.monsterX, self.monsterY - 1) and self.preventEscape(self.monsterX, self.monsterY-1) == False:
                    self.monsterY -= 1
            elif random_move == 'd':
                if self.check_obstacle(self.monsterX, self.monsterY + 1) and self.preventEscape(self.monsterX, self.monsterY+1) == False:
                    self.monsterY += 1
            elif random_move == 's':
                if self.check_obstacle(self.monsterX + 1, self.monsterY) and self.preventEscape(self.monsterX+1, self.monsterY) == False:
                    self.monsterX += 1
            time.sleep(0.21)

    def movement(self):
        while self.stop != True:
            key_pressed = self.client_socket.recv(1024).decode('utf-8')
            if key_pressed.lower() == 'quit':
                self.stop = True
                break
            if key_pressed == 'w':
                if self.check_obstacle(self.playerX - 1, self.playerY):
                    self.playerX -= 1
            elif key_pressed == 'a':
                if self.check_obstacle(self.playerX, self.playerY - 1):
                    self.playerY -= 1
            elif key_pressed == 'd':
                if self.check_obstacle(self.playerX, self.playerY + 1):
                    self.playerY += 1
            elif key_pressed == 's':
                if self.check_obstacle(self.playerX + 1, self.playerY):
                    self.playerX += 1
            if (self.caught()):
                break
            if self.exit():
                break

    def start_monster_movement_thread(self):
        monster_movement_thread = threading.Thread(
            target=self.monster_movement)
        monster_movement_thread.start()

    def start_player_movement_thread(self):
        player_movement_thread = threading.Thread(target=self.movement)
        player_movement_thread.start()


def handle_client(client_socket, addr):
    print(f"Player {addr} started a game !")
    game = Game(10, 10, client_socket, addr)
    game.start_monster_movement_thread()
    game.start_player_movement_thread()

    game_movement_thread = threading.Thread(target=game.movement)
    game_movement_thread.start()
    game_movement_thread.join()
    print(f"Player {addr} finished the game !")


if __name__ == "__main__":
    while True:
        client_socket, addr = server_socket.accept()
        client_handler = threading.Thread(
            target=handle_client, args=(client_socket, addr))
        client_handler.start()
