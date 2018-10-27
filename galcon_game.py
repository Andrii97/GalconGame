import os
import sys
import pygame
from galcon_view import GalconView
from galcon_network import GalconNetwork


class GalconGame():
    def __init__(self, width, height):
        self.width = width
        self.height = height

        pygame.init()

        # initialize the screen
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Galcon-Client-Team-3")

        # initialize in-game clock
        self.clock = pygame.time.Clock()

        self.view = GalconView(self.width, self.height)

    def update(self):

        # sleep to make the game 60 fps
        self.clock.tick(60)

        # clear the screen
        self.screen.fill(0)

        self.view.draw(self.screen)

        for event in pygame.event.get():

            # quit if the quit button was pressed
            if event.type == pygame.QUIT:
                exit()

        # update the screen
        pygame.display.flip()


def main():
    game = GalconGame(800, 600)
    while True:
        game.update()


if __name__ == '__main__':
    main()
