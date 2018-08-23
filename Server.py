import zmq
import sys
import pygame


def main():
    if len(sys.argv) != 1:
        print("Must be called with no arguments")
        exit()

    context = zmq.Context()
    socket = context.socket(zmq.ROUTER)
    socket.bind("tcp://*:4444")

    print("Started server")

    players = {}
    while True:
        ident, dest, msg = socket.recv_multipart()
        data = msg.decode("utf-8").split("$")
        print("Message received from {}".format(ident))
        print (dest, msg)
        if data[0] == "connect":
            print(players)
            players[ident] = True
            socket.send_multipart([msg, ident, dest])
        if data[0] == "Izquierda":
            socket.send_multipart([msg, ident, dest])

if __name__ == '__main__':
    main()
