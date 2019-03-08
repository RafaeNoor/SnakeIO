# Client Code

import time
import random
import curses



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

    help = str(len(snake.body))

    for (x,y) in snake.body:
        stdscr.addstr(y,x,"#")
        stdscr.addstr(10,10,str(snake.body))

    stdscr.addstr(11,11,"("+str(curses.LINES)+","+str(curses.COLS)+")")
    
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

    time.sleep(sleeptime)

curses.endwin()


    

    
