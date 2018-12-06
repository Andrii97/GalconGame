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

planets = {
    COLORRED : planet_red_img,
    COLORGREEN: planet_green_img,
    COLORBLUE: planet_blue_img
}

class GameView(Menu):
    def __init__(self, w, h, screen, user):
        self.w = w
        self.h = h
        self.screen = screen
        self.user = user
        self.bg = pg.Surface((w, h))
        self.star_bg()
        self.planets = []
        self.active_planet = None
    
    def accept_planets(self, planets):
        for planet in planets:
            self.planets.append(planet)
    
    def draw(self, screen, user):
        for planet in self.planets:
            planet.draw(screen)
        pg.display.update()

    def draw_info(self, screen):
        rect = pg.Rect(0,self.h - 100, 300, 100)
        screen.fill((0, 0, 0), rect)
        pg.draw.rect(screen, pg.Color("red"), rect, 1)
        if self.active_planet is not None:
            text_image, _ = Menu.LABELFONT.render("Planet info: " + self.active_planet.owner.name, pg.Color("red"))
            screen.blit(text_image, (10, self.h - 80))

    def mouse_move(self, event):
        x, y = event.pos
        self.active_planet = None
        for planet in self.planets:
            if ((x - planet.pos_x) ** 2 + (y - planet.pos_y) ** 2) < planet.radius ** 2:
                self.active_planet = planet
                break

    def timer_fired(self):
        pass

    def mouse_down(self, event):
        pass

    def mouse_up(self, event):
        pass

    def key_pressed(self, event):
        pass

    def redraw(self, screen):
        self.draw(screen, self.user)
        self.draw_info(screen)
        
    

    def generate_mocked_planets(self, player, enemies): 
        planets = []
        # for current player
        planets.append(Planet(1, 100, 100, randint(30, 60), player))
        planets.append(Planet(2, 400, 200, randint(30, 60), player))

        # for enemies
        planets.append(Planet(3, 720, 200, randint(30, 100), enemies[0]))
        planets.append(Planet(3, 850, 600, randint(30, 100), enemies[1]))

        return planets

class Planet(pg.sprite.Sprite):

    def __init__(self, id, x, y, radius, owner):
        pg.sprite.Sprite.__init__(self)
        self.id = id
        self.pos_x = x
        self.pos_y = y
        self.radius = radius
        self.owner = owner

        # load sprite for image, 
        self.img = self.__load_image_for_color__()

        self.rect = self.img.get_rect()
        self.rect.center = (x, y)

    def draw(self, screen):
        screen.blit(self.img, self.rect)

    def __load_image_for_color__(self):
        img = planets.get(self.owner.color, planet_blue_img)
        img = pg.transform.scale(img, (self.radius * 2, self.radius * 2))
        return img
