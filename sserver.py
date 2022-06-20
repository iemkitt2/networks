import pygame
import random
import pickle
import socket
import threading

WINWIDTH, WINHEIGHT = (1400, 1000)

#Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
DARKRED = (139, 0, 0)
GREEN = (0, 255, 0)
DARKGREEN = (0, 139, 0)
BLUE = (0, 0, 255)
DARKBLUE = (0, 0, 139)

BLOCKSIZE = 20

FPS = 20

class Block:
    def __init__(self, x, y, border=True, color=BLACK, borderColor=WHITE):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, BLOCKSIZE, BLOCKSIZE)
        self.color = color
        self.border = border

        if self.border:
            self.borderColor = borderColor
            self.borderTop = pygame.Rect(self.x, self.y, BLOCKSIZE, BLOCKSIZE / 10)
            self.borderLeft = pygame.Rect(self.x, self.y, BLOCKSIZE / 10, BLOCKSIZE)
            self.borderBottom = pygame.Rect(self.x, self.y + (BLOCKSIZE - BLOCKSIZE / 10), BLOCKSIZE, BLOCKSIZE / 10)
            self.borderRight = pygame.Rect(self.x + (BLOCKSIZE - BLOCKSIZE / 10), self.y, BLOCKSIZE / 10, BLOCKSIZE)

    def updateRect(self):
        self.rect = pygame.Rect(self.x, self.y, BLOCKSIZE, BLOCKSIZE)
        if self.border:
            self.borderTop = pygame.Rect(self.x, self.y, BLOCKSIZE, BLOCKSIZE / 10)
            self.borderLeft = pygame.Rect(self.x, self.y, BLOCKSIZE / 10, BLOCKSIZE)
            self.borderBottom = pygame.Rect(self.x, self.y + (BLOCKSIZE - BLOCKSIZE / 10), BLOCKSIZE, BLOCKSIZE / 10)
            self.borderRight = pygame.Rect(self.x + (BLOCKSIZE - BLOCKSIZE / 10), self.y, BLOCKSIZE / 10, BLOCKSIZE)

    def draw(self, WIN):

        pygame.draw.rect(WIN, self.color, self.rect)

        if self.border:
            pygame.draw.rect(WIN, self.borderColor, self.borderTop)
            pygame.draw.rect(WIN, self.borderColor, self.borderLeft)
            pygame.draw.rect(WIN, self.borderColor, self.borderRight)
            pygame.draw.rect(WIN, self.borderColor, self.borderBottom)

class Player:
    def __init__(self, startX, startY, color=BLUE, borderColor=DARKBLUE, startLen=3):
        self.color = color
        self.borderColor = borderColor

        self.snake = [Block(startX, startY, color=self.color, borderColor=self.borderColor)]
        for i in range(startLen):
            self.snake.append(Block(self.snake[-1].x - BLOCKSIZE, self.snake[-1].y, color=self.color, borderColor=self.borderColor))
        self.direction = "RIGHT"

        self.score = 0

    def move(self, move=None):

        if move == "LEFT" and self.direction != "RIGHT":
            self.direction = "LEFT"
            self.snake[0].x -= BLOCKSIZE
        elif move == "RIGHT" and self.direction != "LEFT":
            self.direction = "RIGHT"
            self.snake[0].x += BLOCKSIZE
        elif move == "UP" and self.direction != "DOWN":
            self.direction = "UP"
            self.snake[0].y -= BLOCKSIZE
        elif move == "DOWN" and self.direction != "UP":
            self.direction = "DOWN"
            self.snake[0].y += BLOCKSIZE
        else:
            move == None

        if move == None:
            if self.direction == "RIGHT":
                self.snake[0].x += BLOCKSIZE
            elif self.direction == "LEFT":
                self.snake[0].x -= BLOCKSIZE
            elif self.direction == "UP":
                self.snake[0].y -= BLOCKSIZE
            elif self.direction == "DOWN":
                self.snake[0].y += BLOCKSIZE

        if self.snake[0].x >= WINWIDTH:
            self.snake[0].x = 0
        if self.snake[0].x < 0:
            self.snake[0].x = WINWIDTH - BLOCKSIZE
        if self.snake[0].y >= WINHEIGHT:
            self.snake[0].y = 0
        if self.snake[0].y < 0:
            self.snake[0].y = WINHEIGHT - BLOCKSIZE

        for part in self.snake[::-1]:
            if self.snake.index(part) != 0:
                part.x = self.snake[self.snake.index(part) - 1].x
                part.y = self.snake[self.snake.index(part) - 1].y

    def draw(self, WIN):
        for part in self.snake:
            part.updateRect()
            part.draw(WIN)

    def addPiece(self):

        if self.direction == "RIGHT":
            self.snake.append(Block(self.snake[-1].x - BLOCKSIZE, self.snake[-1].y, color=self.color, borderColor=self.borderColor))
        elif self.direction == "LEFT":
            self.snake.append(Block(self.snake[-1].x + BLOCKSIZE, self.snake[-1].y, color=self.color, borderColor=self.borderColor))
        elif self.direction == "UP":
            self.snake.append(Block(self.snake[-1].x, self.snake[-1].y + BLOCKSIZE, color=self.color, borderColor=self.borderColor))
        elif self.direction == "DOWN":
            self.snake.append(Block(self.snake[-1].x, self.snake[-1].y - BLOCKSIZE, color=self.color, borderColor=self.borderColor))

class Food(Block):
    def __init__(self, INDEX, color=GREEN, borderColor=DARKGREEN):
        super().__init__(random.randint(0, (WINWIDTH - BLOCKSIZE) / BLOCKSIZE) * BLOCKSIZE, random.randint(0, (WINHEIGHT - BLOCKSIZE) / BLOCKSIZE) * BLOCKSIZE, color=color, borderColor=borderColor)
        self.index = INDEX

class DISCONNECTOBJ:
    def __init__(self):
        pass

class GameServer:
    def __init__(self, PORT=31705):

        self.PORT = PORT
        self.SERVER = socket.gethostbyname(socket.gethostname())
        self.ADDRESS = (self.SERVER, self.PORT)

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.ADDRESS)

        self.players = [Player(200, 200), Player(500, 500, color=RED, borderColor=DARKRED)]
        self.food = Food(0)

        self.start()

    def start(self):
        self.server.listen()

        print("[SERVER]: Listening on {0}".format(self.SERVER))

        while True:
            connection, address = self.server.accept()
            thread = threading.Thread(target=self.handleClient, args=(connection, address, threading.activeCount()))
            thread.start()
            print("[SERVER]: {0} active connections.".format(threading.activeCount() - 1))

    def handleClient(self, conn, addr, playerNum):

        #On Connection Logic
        if playerNum == 1:
            self.send(self.players[0], conn)
            self.send(self.players[1], conn)
        elif playerNum == 2:
            self.send(self.players[1], conn)
            self.send(self.players[0], conn)

        self.send(self.food, conn)

        connected = True
        while connected:

            obj = self.rec(conn)

            if type(obj) == DISCONNECTOBJ:
                connected = False
                break

            if type(obj) == Player:
                if playerNum == 1:
                    self.players[0] = obj
                    self.send(self.players[1], conn)
                elif playerNum == 2:
                    self.players[1] = obj
                    self.send(self.players[0], conn)

            if type(obj) == Food:
                self.food = obj

                self.send(self.food, conn)

        conn.close()

    def send(self, obj, conn):
        conn.send(pickle.dumps(obj))

    def rec(self, conn):

        obj = pickle.loads(conn.recv(20000))
        return obj