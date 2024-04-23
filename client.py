import socket
import threading
import os
import pickle

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
address = input("Server address : ")
client_socket.connect((address, 5050))

stop = False


def display_lab(current):
    for i in range(current['rows']):
        for j in range(current['cols']):
            if i == current['playerX'] and j == current['playerY']:
                print("🎅 ", end='')
            elif i == current['monsterX'] and j == current['monsterY']:
                print("😈 ", end='')
            else:
                print(current['matrix'][i][j] + "  ", end='')
        print()


def display_thread():
    while True:
        received_data = client_socket.recv(4096)
        os.system('cls' if os.name == 'nt' else 'clear')
        current = pickle.loads(received_data)
        if 'status' in current:
            print(current['message'])
            client_socket.close()
            os._exit(0)
        display_lab(current)


def input_thread():
    while True:
        user_input = input()
        client_socket.send(user_input.encode('utf-8'))
        if user_input.lower() == 'quit':
            print("Revin-o oricand 😉 !")
            os._exit(0)


input_handler = threading.Thread(target=input_thread)
display_handler = threading.Thread(target=display_thread)

input_handler.start()
display_handler.start()

input_handler.join()
display_handler.join()

client_socket.close()
