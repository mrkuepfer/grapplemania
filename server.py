# Grapple race server

import socket
import pickle

from constants import *
from level import *


level_file = input("Enter level file: ")
hosted_level = Level(SAVES_FOLDER + level_file + SAVES_EXT)

PACKET_SIZE = 2048

HOST = socket.gethostbyname(socket.gethostname())
PORT = 9999

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))

players = {}

while True:
    message, address = sock.recvfrom(PACKET_SIZE*2)
    data = pickle.loads(message)
    ip = address[0]
    if data["type"] == "connect":
        print(ip, "trying to connect")
        players[ip] = {}
        response = {"success": True,
                    "level": hosted_level,
                    "ip": ip}
    
    elif data["type"] == "update":
        players[ip] = data["player_data"]
        response = {"success": True,
                    "players": players}

    elif data["type"] == "disconnect":
        print(ip, "disconnected")
        if ip in players:
            players.pop(ip)
        
    else:
        response = {"success": False}

    binary = pickle.dumps(response)
    size = len(binary)
    if size < PACKET_SIZE:
        # data fits in one packet
        message = {"type": "single", "binary": binary}
        sock.sendto(pickle.dumps(message), address)
    else:
        # split data into multiple packets
        for i in range(size//PACKET_SIZE+1):
            chunk = binary[PACKET_SIZE*i:PACKET_SIZE*(i+1)]
            message = {"type": "multipart", "binary": chunk, "num": i, "len": size//PACKET_SIZE+1}
            sock.sendto(pickle.dumps(message), address)
            
            

