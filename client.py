import sserver
import pickle
import pygame
import sys
import socket

pygame.init()
WIN = pygame.display.set_mode((1400, 1000))

class GameClient:
    def __init__(self, SERVER, PORT=31705):

        self.PORT = PORT
        self.SERVER = SERVER
        self.ADDRESS = (self.SERVER, self.PORT)

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(self.ADDRESS)

        self.CLOCK = pygame.time.Clock()

        self.players = [self.rec(), self.rec()]
        self.food = self.rec()

        self.main()

    def send(self, obj):
        self.client.send(pickle.dumps(obj))

    def rec(self):
        return pickle.loads(self.client.recv(20000))

    def draw(self):

        WIN.fill(sserver.BLACK)

        for player in self.players:
            player.draw(WIN)

        self.food.draw(WIN)

        pygame.display.update()

    def main(self):

        gameOver = False
        while not gameOver:

            move = None
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.send(sserver.DISCONNECTOBJ())
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        move = "RIGHT"
                    if event.key == pygame.K_LEFT:
                        move = "LEFT"
                    if event.key == pygame.K_UP:
                        move = "UP"
                    if event.key == pygame.K_DOWN:
                        move = "DOWN"


            self.players[0].move(move=move)


            if self.players[0].snake[0].rect.colliderect(self.food.rect):
                self.players[0].addPiece()
                self.food = sserver.Food(0)

            self.send(self.food)
            self.food = self.rec()


            self.send(self.players[0])
            self.players[1] = self.rec()
            #print("POS: ({0}, {1})".format(self.players[0].snake[0].x, self.players[0].snake[0].y))

            self.draw()
            self.CLOCK.tick(sserver.FPS)

c =GameClient("192.168.1.4")