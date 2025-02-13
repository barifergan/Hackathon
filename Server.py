import concurrent.futures
import random
import socket
import threading
import time
import struct

global to_listen
BROADCAST = '<172.1.255.255>'
CPINK = '\33[91m'
CEND = '\33[0m'
PACKET_FORMAT = 'Ibh'
TCP_PORT_NUM = 2053
UDP_PORT_NUM = 13117
BUFFER_SIZE = 1024
CGREEN = '\33[92m'


class Server:
    def __init__(self):
        #initiolize the server , opens a thread for sending UDP messages
        self.all_clients = {} #connected clients
        self.init_thread = threading.Thread(target=self.send_in_broadcast)
        self.init_thread.start()


    def send_in_broadcast(self):

        global to_listen
        to_listen = True
        listen_thread = threading.Thread(target=self.server_listen)
        listen_thread.start()
        PORT_NUM = 2053
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        print(CPINK + 'Server started,listening on IP address', socket.gethostbyname(socket.gethostname()) + CEND)
        global dead
        dead = False
        message = struct.pack(PACKET_FORMAT, 0xfeedbeef, 0x2, PORT_NUM)
        while not dead:
            server.sendto(message, (BROADCAST, UDP_PORT_NUM))
            time.sleep(1)


    def server_listen(self):
        # server listen to TCP_PORT_NUM
        threading.Timer(10, self.play,).start()
        self.all_clients = {}
        while to_listen:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("", TCP_PORT_NUM))
            s.listen()
            try:
                s.settimeout(1)
                connection, client_address = s.accept()
            except:
                continue
            thread = threading.Thread(target=self.serve, args=(connection,))
            thread.start()

    def serve(self,connection):
        team_name = connection.recv(BUFFER_SIZE)
        self.all_clients[connection] = (team_name, random.choice([1, 2]))


    def play(self):
        global to_listen
        to_listen = False
        global dead
        dead = True # stops broadcasting and listening
        if not self.all_clients: #empty game - return to listen and broadcast
            time.sleep(3)
            threading.Thread(target=self.send_in_broadcast).start()
            return

        group1 = []
        group2 = []
        msg = 'Welcome to keyboard spamming Battle Royale.\n'

        for connection in self.all_clients.keys():
            team_num = self.all_clients[connection][1]
            if team_num == 1:
                group1.append(self.all_clients[connection][0])
            else:
                group2.append(self.all_clients[connection][0])

        msg += 'Group 1:\n==\n'
        group1_names = ''
        for team in group1:
            group1_names += team.decode('utf-8') + '\n'
        msg += group1_names

        msg += 'Group 2:\n==\n'
        group2_names = ''
        for team in group2:
            group2_names += team.decode('utf-8') + '\n'

        msg += group2_names
        msg += '\nStart pressing keys on your keyboard as fast as you can!!'

        for connection in self.all_clients.keys():
            connection.send(msg.encode())

        # start operating the game - using futures to collect clients scores
        futures_of_team1 = []
        futures_of_team2 = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for connection in self.all_clients.keys():
                future = executor.submit(self.start_new_game, connection)
                if self.all_clients[connection][1]  ==1:
                    futures_of_team1.append(future)
                else:
                    futures_of_team2.append(future)

        result_team1 = sum([res.result() for res in futures_of_team1])
        result_team2 = sum([res.result() for res in futures_of_team2])

        if result_team1 > result_team2:
            winner = 1
            win_group = group1_names
            win_msg = 'Group ' + str(winner) + ' wins!\n\nCongratulations to the winners:\n==\n' + win_group
        elif result_team2 > result_team1:
            winner = 2
            win_group = group2_names
            win_msg = 'Group ' + str(winner) + ' wins!\n\nCongratulations to the winners:\n==\n' + win_group
        else:
            win_msg = 'Its a draw!'

        game_over = 'Game over!\nGroup 1 typed in ' + str(result_team1) + ' characters. Group 2 typed in ' + str(
            result_team2) + ' characters.\n'


        game_over_msg = CGREEN + game_over + win_msg + CEND

        for client in self.all_clients.keys():
            try:# if the client disconnected
                client.send(bytes(game_over_msg, 'utf-8'))
                time.sleep(1)
                client.close()
            except:
                continue

        print(CPINK + '\nGame over, sending out offer requests...' + CEND)
        time.sleep(2)
        threading.Thread(target=self.send_in_broadcast).start()

    def start_new_game(self, connection):
        char_counter = 0
        connection.settimeout(10)
        start_time = time.time()
        while time.time() - start_time < 10:
            try:
                connection.recv(BUFFER_SIZE).decode()
                char_counter += 1

            except:
                pass
        return char_counter

if __name__ == '__main__':
    server = Server()


