import pygame as pg


class GalconView():
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.menu_img = pg.image.load("materials/1.png")


    def draw(self, screen):
        screen.blit(self.menu_img, [0, 0])
