import pygame as pg
import pygame.sprite as sp
from random import randint
from menu import Menu
from numpy import (array, dot, arccos, clip)
from numpy.linalg import norm
import math

planet_red_img = pg.image.load('materials/planet_red.png')
planet_green_img = pg.image.load('materials/planet_green.png')
planet_blue_img = pg.image.load('materials/planet_blue.png')
ship_pink_img = pg.image.load('materials/ship_1.png')

COLORRED = (255, 0, 0)
COLORGREEN = (0, 255, 0)
COLORBLUE = (0, 0, 255)

planets = {
    COLORRED: planet_red_img,
    COLORGREEN: planet_green_img,
    COLORBLUE: planet_blue_img
}


class GameView(Menu):
    def __init__(self, w, h, screen, user, main_menu):
        self.w = w
        self.h = h
        self.screen = screen
        self.user = user
        self.main_menu = main_menu
        self.buttons = sp.RenderUpdates()
        self.statusBoxDict = dict()
        self.statusBoxes = sp.RenderUpdates()
        self.bg = pg.Surface((w, h))
        self.star_bg()
        self.planets = []
        self.ships = []
        self.active_planet = None
        self.start_planet = None
        self.end_planet = None
        self.group_size = 10
        self.pressed = None
        self.exit_menu_shown = False

        self.add_status_box("status", "Exit to main menu?", w // 2, h // 2 - 50)
        self.add_button("EXIT", pg.Rect((w - 300) // 2, (h - 50) // 2, 300, 50), self.main_menu)
        self.add_button("BACK", pg.Rect((w - 300) // 2, (h - 50) // 2 + 60, 300, 50), self.hide_exit_menu)

    def accept_planets(self, planets):
        for planet in planets:
            self.planets.append(planet)

    def accept_ships(self, ships):
        for ship in ships:
            self.ships.append(ship)

    def draw(self, screen, user):
        for planet in self.planets:
            planet.draw(screen)
        pg.display.update()

    def draw_exit_menu(self, screen):
        if self.exit_menu_shown:
            self.buttons.draw(screen)
            self.statusBoxes.draw(screen)

    def hide_exit_menu(self):
        self.exit_menu_shown = False
        self.buttons.clear(self.screen, self.bg)
        self.statusBoxes.clear(self.screen, self.bg)

    def draw_info(self, screen):
        rect = pg.Rect(0, self.h - 100, 300, 100)
        screen.fill((0, 0, 0), rect)
        pg.draw.rect(screen, pg.Color("red"), rect, 1)
        if self.active_planet is not None:
            text_image, _ = Menu.LABELFONT.render("Planet owner: " + self.active_planet.owner.name + "  Ships: " \
                                                  + str(self.active_planet.ships), pg.Color("red"))
            screen.blit(text_image, (10, self.h - 80))

    def mouse_move(self, event):
        x, y = event.pos
        self.active_planet = None
        for planet in self.planets:
            if ((x - planet.pos_x) ** 2 + (y - planet.pos_y) ** 2) < planet.radius ** 2:
                self.active_planet = planet
                break

        for but in self.buttons:
            if but.contains_pt(event.pos):
                but.mouse_over()
            else:
                but.un_mouse_over()

    def timer_fired(self):
        pass

    def mouse_down(self, event):
        if self.exit_menu_shown:
            for but in self.buttons:
                if but.contains_pt(event.pos):
                    self.pressed = but
                    but.press()

    def mouse_up(self, event):
        if self.active_planet is not None:
            if self.active_planet.owner_name == 'User' and self.start_planet == None:
                self.start_planet = self.active_planet
            elif self.start_planet != None:
                self.end_planet = self.active_planet
                self.send_ships(self.start_planet, self.end_planet, 1)
                self.start_planet = None
                self.end_planet = None

        if self.pressed:
            if self.pressed.contains_pt(event.pos):
                self.pressed.release()
                self.pressed = None

            else:
                self.pressed.unpress()
                self.pressed = None

    def key_pressed(self, event):
        if event.key == pg.K_ESCAPE:
            self.exit_menu_shown = True

    def redraw(self, screen):
        self.draw(screen, self.user)
        self.draw_info(screen)
        self.draw_exit_menu(screen)

    def generate_mocked_planets(self, player, enemies):
        planets = []
        # for current player
        planets.append(Planet(1, 100, 100, randint(30, 60), player, 'User'))
        planets.append(Planet(2, 400, 200, randint(30, 60), player, 'User'))

        # for enemies
        planets.append(Planet(3, 700, 300, randint(30, 100), enemies[0], 'Enemy'))
        planets.append(Planet(3, 850, 600, randint(30, 100), enemies[1], 'Enemy'))

        return planets

    def send_ships(self, start_planet, end_planet, counter):
        ships = []

        vector = [end_planet.pos_x - start_planet.pos_x, end_planet.pos_y - start_planet.pos_y]
        comp_vector = [start_planet.radius, 0]

        if end_planet.pos_x > start_planet.pos_x:
            sign1 = 1
        elif end_planet.pos_x < start_planet.pos_x:
            sign1 = -1
        else:
            sign1 = 0

        if end_planet.pos_y > start_planet.pos_y:
            sign2 = 1
        elif end_planet.pos_y < start_planet.pos_y:
            sign2 = -1
        else:
            sign2 = 0

        cos = dot(comp_vector, vector) / norm(comp_vector) / norm(vector)
        sin = math.sqrt(1 - cos ** 2)

        temp_x = start_planet.pos_x + start_planet.radius * cos
        temp_y = start_planet.pos_y + start_planet.radius * sin * sign2

        print(sign1, sign2)

        destination = [end_planet.pos_x, end_planet.pos_y]

        direction = [start_planet.radius * cos, sign2 * start_planet.radius * sin]

        for i in range(0, counter):
            ships.append(Ship(i, temp_x, temp_y, direction, destination, start_planet.owner, start_planet.owner_name))
            temp_x += 5
            temp_y += 5

        self.accept_ships(ships)


class Planet(pg.sprite.Sprite):

    def __init__(self, id, x, y, radius, owner, name):
        pg.sprite.Sprite.__init__(self)
        self.id = id
        self.pos_x = x
        self.pos_y = y
        self.radius = radius
        self.owner = owner
        self.owner_name = name
        self.ships = 100
        self.gen_speed = 1

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


class Ship(pg.sprite.Sprite):

    def __init__(self, id, x, y, direction, destination, owner, name):
        pg.sprite.Sprite.__init__(self)
        self.id = id
        self.pos_x = x
        self.pos_y = y
        self.owner = owner
        self.owner_name = name
        self.destination = destination
        self.direction = direction
        self.radius = 15

        self.mov_speed_init = 10
        self.mov_speed = self.mov_speed_init

        self.img = self.__load_image_for_color__()
        self.rect = self.img.get_rect()
        self.rect.center = (self.pos_x, self.pos_y)
        self.reached = False

    def update(self, screen):

        if (abs(self.pos_x - self.destination[0]) + abs(self.pos_y - self.destination[1]) >= 30):
            self.pos_x += self.direction[0] / 10
            self.pos_y += self.direction[1] / 10
        else:
            self.reached = True
        self.rect.center = (self.pos_x, self.pos_y)
        self.draw(screen)

    def draw(self, screen):
        screen.blit(self.img, self.rect.center)

    def __load_image_for_color__(self):
        img = ship_pink_img
        img = pg.transform.scale(img, (self.radius * 2, self.radius * 2))
        return img
