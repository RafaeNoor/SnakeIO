#!/usr/bin/env python3
import asyncio
import json
import pickle

numCon = 0 # number of connections made with the server
conList = [] # list of connections made to the server (can use len(conList) to get former


HOST = '127.0.0.1'
PORT = 8888

class SnakeServerProtocol(asyncio.Protocol):

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport

        self.transport.write(pickle.dumps({"mode":"user","player": str(peername),"name":str(peername)}))


        global numCon
        numCon += 1

        global conList
        conList.append(self.transport)
        print('Number of Connections: {}'.format(numCon))

        self.send_all(pickle.dumps({"mode":"add","player":str(peername)}))


    def connection_lost(self, exc):
        print('Lost a connection from client...')
        global numCon
        numCon -= 1

        conList.remove(self.transport)
        print('Number of Connections: {}'.format(numCon))


    def data_received(self, data):
        message = pickle.loads(data) 
        #print('Data received from {}:{!r}'.format(self.transport.get_extra_info('peername'),message),type(message))

        if isinstance(message,dict):
            if message["mode"] == "move":
                prepare =  {"player":str(self.transport.get_extra_info('peername')), "body": message["body"],"mode":"move"}
                packet = pickle.dumps(prepare) #  Arbritrary dictionary for snake game
                #print("Sending",prepare)
                self.send_all(packet)
            elif message["mode"] == "dead":
               print("Disconnecting player...") 
               packet = {"mode":"dead","player":str(self.transport.get_extra_info('peername'))}
               self.send_all(pickle.dumps(packet))
        else:
            print(message)

    def send_all(self,data):
        global conList
        for con in conList:
            con.write(data)


async def main():
    loop = asyncio.get_running_loop()

    numCon = 0
    server = await loop.create_server(
            lambda: SnakeServerProtocol(),
            HOST, PORT)

    async with server:
        await server.serve_forever()


try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\n--> Closing server...")
