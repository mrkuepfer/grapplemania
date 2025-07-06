# Grapple race client tools

import pickle
import socket
import sys
from player import Player

PACKET_SIZE = 2048

class Connection:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.ip = None
        self.players = {}
        self.status = "available"

        # Attempt to connect and load level
        message = {"type": "connect"}
        self.send(message)
        response = self.receive()
        if response and response["success"]:
            self.level = response["level"]
            self.ip = response["ip"]
        else:
            print("Failed to connect")
            
    def send(self, data):
        """
        Sends data to the connected server, setting status to 'waiting'.
        """
        self.status = "waiting"
        self.socket.sendto(pickle.dumps(data), (self.host, self.port))

    def receive(self):
        """
        Receives data from connected server. If the data is too large to fit in one packet, will automatically
        wait for a multipart series of packets and combine them. Sets status to 'available'.
        """ 
        message = pickle.loads(self.socket.recv(PACKET_SIZE*2))
        try:
            if message["type"] == "single":
                self.status = "available"
                return pickle.loads(message["binary"])
            elif message["type"] == "multipart":
                full_binary = b''
                success = True
                for i in range(message["len"]):
                    if message["num"] != i:
                        print("dropped multipart message part", i, "of", message["len"], ", got", message["num"])
                        success = False
                    else:
                        full_binary += message["binary"]
                    if i != message["len"]-1:
                        message = pickle.loads(self.socket.recv(PACKET_SIZE*2))
                if success:
                    self.status = "available"
                    return pickle.loads(full_binary)
            self.status = "available"
        except KeyError:
            print(message)
                

    def update_players(self, response_data):
        for ip, data in response_data.items():
            if ip in self.players and self.players[ip] != {}:
                self.players[ip].x = data["x"]
                self.players[ip].y = data["y"]
                self.players[ip].grapple = data["grapple"]
            else:
                self.players[ip] = Player(self.level, data["x"], data["y"])

    def update(self, player):
        if self.status == "available":
            message = {"type": "update",
                       "ip": self.ip,
                       "player_data": {"x": player.x,
                                       "y": player.y,
                                       "grapple": player.grapple}}
            self.send(message)
            response = self.receive()
            if response:
                self.update_players(response["players"])
                return True
            else:
                print("Did not receive response.")
                return False
        else:
            return False

    def disconnect(self):
        message = {"type": "disconnect",
                   "ip": self.ip}
        self.send(message)

    def __del__(self):
        self.disconnect()

