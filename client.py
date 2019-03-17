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




counter = 0
done = False
move = 'right'

server_message = ""


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


        head_x,head_y = snake.getCoord()
        stdscr.addstr(head_y,head_x,"@")


        for (x,y) in snake.body:
            stdscr.addstr(y,x,"#")
            #stdscr.addstr(10,10,str(snake.body))

        stdscr.addstr(11,11,"("+str(curses.LINES)+","+str(curses.COLS)+")")

        global counter
        stdscr.addstr(10,20,str(counter))

        key = stdscr.getch()

        global move

        if key == curses.KEY_DOWN:
            snake.vx = 0
            snake.vy = 1
            move = "down"
        elif key == curses.KEY_UP:
            snake.vx = 0
            snake.vy = -1
            move = "up"
        elif key == curses.KEY_LEFT:
            snake.vx = -1
            snake.vy = 0
            move = "left"
        elif key == curses.KEY_RIGHT:
            snake.vx = 1
            snake.vy = 0
            move = "right"

        alive = snake.checkAlive()

        snake.updatePos()

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
        js = pickle.loads(data) # string to json

        global server_message
        server_message = js



    def connection_lost(self, exc):
        self.on_con_lost.set_result(True)


async def updateDone():
    loop = asyncio.get_running_loop()
    on_con_lost = loop.create_future()

    transport, protocol = await loop.create_connection(
            lambda: SnakeClientProtocol('Pinging server', on_con_lost, loop),
            HOST, PORT)

    old_move = ""

    global done
    while not done:
        await asyncio.sleep(1)
        global counter
        global server_message
        global move
        
        counter += 1

        packet = {"counter":counter,"move":move, 
                "done":done}
        if old_move != move: # Update only if move changed OR whenever we deem necessary
            transport.write(pickle.dumps(packet));
            old_move = move



def alt_thread(): # testing if threads can mutate global variables (answer is yes)
    asyncio.run(updateDone());


#  Game running Locally
main_thread = threading.Thread(target = main, args = ())
#  Asycronous Server Communication
another = threading.Thread(target = alt_thread, args = ())

#  Start Both Threads
main_thread.start()
another.start()
