# Client Code

import time
import random
import curses
import socket
import asyncio
import threading
import pickle

HOST = '127.0.0.1'
PORT = 8888 




done = False
opponents = {}



class Snake(object):
    def __init__(self):
        self.head_x = random.randint(10,50)
        self.head_y = random.randint(10,50)
        self.len = 10
        self.body = [(self.head_x - (i+1),self.head_y) for i in range(0,self.len)] 
        self.vx = 1
        self.vy = 0

    def getCoord(self):
        return self.head_x, self.head_y
    def getBody(self):
        return [(self.head_x,self.head_y)] + self.body

    def updatePos(self):
        for i in range(self.len-1,0,-1):
            self.body[i] = self.body[i-1]
        self.body[0] = (self.head_x,self.head_y)

        self.head_x += self.vx
        self.head_y += self.vy

    def checkAlive(self):
        out_of_bounds = not ((self.head_x > 0 and self.head_x < curses.COLS -2 ) and (self.head_y >0 and self.head_y < curses.LINES -2))

        full_snake = [(self.head_x,self.head_y)] + self.body
        self_collision = len(full_snake) != len(set(full_snake)) 

        if out_of_bounds:
            return False
        elif self_collision:
            return False
        else:
            return True




fps = 10 

sleeptime = 1/fps


body = []

def main():
    stdscr = curses.initscr()
    curses.cbreak()
    curses.curs_set(0)
    stdscr.keypad(1)
    stdscr.timeout(100)

    snake = Snake()

    alive = True


    while alive:
        stdscr.refresh()
        stdscr.clear()

        for i in range(0,curses.COLS):
            stdscr.addstr(0,i,"=")
            stdscr.addstr(curses.LINES-2,i,"=")

        for j in range(0,curses.LINES):
            stdscr.addstr(j,0,"+")
            stdscr.addstr(j,curses.COLS-2,"+")

        for opp,bd in opponents.items(): #opponents includes rendering me as well
            if bd == []:
                continue

            #Could add collision with other check here. Check if my head == other posision

            (o_x,o_y) = bd[0]
            stdscr.addstr(o_y,o_x,"@")
            for (x,y) in bd[1:]:
                stdscr.addstr(y,x,"#")



        key = stdscr.getch()


        if key == curses.KEY_DOWN:
            snake.vx = 0
            snake.vy = 1
        elif key == curses.KEY_UP:
            snake.vx = 0
            snake.vy = -1
        elif key == curses.KEY_LEFT:
            snake.vx = -1
            snake.vy = 0
        elif key == curses.KEY_RIGHT:
            snake.vx = 1
            snake.vy = 0

        alive = snake.checkAlive()


        snake.updatePos()

        global body
        body = snake.getBody()

        time.sleep(sleeptime)

    curses.endwin()
    global done
    done = True


class SnakeClientProtocol(asyncio.Protocol):

    def __init__(self, message, on_con_lost, loop):
        self.message = message
        self.loop = loop
        self.on_con_lost = on_con_lost


    def connection_made(self, transport):
        transport.write(pickle.dumps(self.message))
        self.transport = transport



    def data_received(self, data):
        content = pickle.loads(data) # string to json
        global opponents

        if content["mode"] == "add":
            #if content["player"] == str(self.transport.get_extra_info('peername')):
            #    return
            opponents[content["player"]] = []
        elif content["mode"] == "move":
            #print("someone made a move")
            opponents[content["player"]] = content["body"]

            # add collision check
        elif content["mode"] == "dead":
            opponents[content["player"]] = []


    def connection_lost(self, exc):
        self.on_con_lost.set_result(True)


async def network_conn():
    loop = asyncio.get_running_loop()
    on_con_lost = loop.create_future()

    transport, protocol = await loop.create_connection(
            lambda: SnakeClientProtocol('Pinging server', on_con_lost, loop),
            HOST, PORT)


    global done
    while not done:
        await asyncio.sleep(0.05)
        global body
        packet = {"mode":"move","body":body}
        transport.write(pickle.dumps(packet))

    await asyncio.sleep(0.5)
    print("Screen Closed")
    transport.write(pickle.dumps({"mode":"dead"}))



def alt_thread(): # testing if threads can mutate global variables (answer is yes)
    asyncio.run(network_conn());


#  Game running Locally
main_thread = threading.Thread(target = main, args = ())
#  Asycronous Server Communication
net = threading.Thread(target = alt_thread, args = ())

#  Start Both Threads
main_thread.start()
net.start()
