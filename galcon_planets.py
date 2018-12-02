import pygame as pg
import pygame.sprite as sp
from random import randint
from menu import Menu

planet_red_img = pg.image.load('materials/planet_red.png')
planet_green_img = pg.image.load('materials/planet_green.png')
planet_blue_img = pg.image.load('materials/planet_blue.png')

COLORRED = (255, 0, 0)
COLORGREEN = (0, 255, 0)
COLORBLUE = (0, 0, 255)


class GameView(Menu):
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.bg = pg.Surface((w, h))
        self.star_bg()
        self.planets = []
    
    def accept_planets(self, planets):
        for planet in planets:
            self.planets.append(planet)
    
    def draw(self, screen, user):
        for planet in self.planets:
            planet.draw(screen)
        pg.display.update()

    def mouse_move(self, event):
        pass

    def timer_fired(self):
        pass

    def mouse_down(self, event):
        pass

    def mouse_up(self, event):
        pass

    def key_pressed(self, event):
        pass

    def redraw(self, screen):
        pass
    

    def generate_mocked_planets(self, player, enemies): 
        planets = []
        # for current player
        planets.append(Planet(1, 100, 100, randint(20, 30), player))
        planets.append(Planet(2, 400, 200, randint(20, 30), player))

        # for enemies
        planets.append(Planet(3, 720, 200, randint(20, 30), enemies[0]))
        planets.append(Planet(3, 850, 600, randint(20, 30), enemies[1]))

        return planets

class PlanetSprite(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        pg.draw.circle(self.image, (255, 0, 0), (150, 200), 25, 0 )
        self.rect = self.image.get_rect()
        self.rect.center = (150, 200)


class Planet(pg.sprite.Sprite):

    def __init__(self, id, x, y, radius, owner):
        pg.sprite.Sprite.__init__(self)
        self.id = id
        self.pos_x = x
        self.pos_y = y
        self.radius = radius
        self.owner = owner
        self.__load_image_for_color__()
        self.rect = self.img.get_rect()
        self.rect.center = (x, y)

    def draw(self, screen):
        screen.blit(self.img, self.rect)

    def __load_image_for_color__(self):
        if self.owner.color == COLORRED:
            self.img = planet_red_img
        elif self.owner.color == COLORGREEN:
            self.img = planet_green_img
        elif self.owner.color == COLORBLUE:
            self.img = planet_blue_img
        else: 
            self.img = planet_green_img
