from random import randint

import pygame as pg
import pygame.sprite as sp

from menu import Menu, Button
from models import Planet, Color


class GameView(Menu):
    def __init__(self, w, h, screen, user, main_menu):
        self.w = w
        self.h = h
        self.screen = screen
        self.user = user
        self.main_menu = main_menu
        self.buttons = sp.RenderUpdates()
        self.menu_buttons = sp.RenderUpdates()
        self.statusBoxDict = dict()
        self.statusBoxes = sp.RenderUpdates()
        self.bg = pg.Surface((w, h))
        self.star_bg()
        self.planets = []
        self.active_planet = None
        self.pressed = None
        self.exit_menu_shown = False
        self.selected_planet = None
        self.clusterNames = {}
        self.ships = sp.RenderUpdates()
        self.power = 0.5

        self.add_status_box("status", "Do you want to exit to main menu?", w // 2, h // 2 - 50)
        self.add_menu_button("YES", pg.Rect((w - 300) // 2, (h - 50) // 2, 300, 50), self.main_menu)
        self.add_menu_button("NO", pg.Rect((w - 300) // 2, (h - 50) // 2 + 60, 300, 50), self.hide_exit_menu)
        self.power_button = self.add_button('{0:.0f}%'.format(self.power * 100), pg.Rect(w - 60, h - 60, 50, 50), self.hide_exit_menu)

    def accept_planets(self, planets):
        for planet in planets:
            self.planets.append(planet)

    def draw(self, screen):
        rects = []
        for planet in self.planets:
            planet.units.update()
            rects += planet.draw(screen)
        self.ships.clear(screen, self.bg)
        rects += self.ships.draw(screen)
        return rects

    def rect_exit_menu(self, screen):
        return self.menu_buttons.draw(screen) + self.statusBoxes.draw(screen)

    def add_menu_button(self, *args):
        self.menu_buttons.add(Button(*args))

    def hide_exit_menu(self):
        self.exit_menu_shown = False

    def draw_info(self, screen):
        rect = pg.Rect(0, self.h - 100, 300, 100)
        screen.fill(Color.BLACK, rect)
        rects = pg.draw.rect(screen, pg.Color("red"), rect, 1)
        if self.active_planet is not None:
            text_image, _ = Menu.LABEL_FONT.render("Planet info: " + self.active_planet.owner.name, pg.Color("red"))
            screen.blit(text_image, (10, self.h - 80))
        return rects

    def mouse_move(self, event):
        x, y = event.pos
        self.active_planet = None
        for planet in self.planets:
            if ((x - planet.pos_x) ** 2 + (y - planet.pos_y) ** 2) < planet.radius ** 2:
                self.active_planet = planet
                break

        for but in self.menu_buttons:
            if but.contains_pt(event.pos):
                but.mouse_over()
            else:
                but.un_mouse_over()

        for but in self.buttons:
            if but.contains_pt(event.pos):
                but.mouse_over()
            else:
                but.un_mouse_over()

    def timer_fired(self):
        # remove empty clusters
        emptyClusters = []
        for i in self.clusterNames:
            if not self.clusterNames[i]:
                emptyClusters.append(i)
        for i in emptyClusters:
            self.clusterNames.pop(i)

        # move ships
        for i in self.clusterNames:
            self.clusterNames[i].move(self.ships, self.planets)

    def mouse_down(self, event):
        if self.exit_menu_shown:
            for but in self.menu_buttons:
                if but.contains_pt(event.pos):
                    self.pressed = but
                    but.press()
        for but in self.buttons:
            if but.contains_pt(event.pos):
                self.pressed = but
                but.press()
                self.change_power()

    def mouse_up(self, event):
        if event.button == 1:  # left click
            if self.active_planet is not None:
                if self.active_planet.owner.name == self.user.name and self.selected_planet is None:
                    self.selected_planet = self.active_planet
                    self.selected_planet.selected = True
                elif self.selected_planet == self.active_planet:
                    self.selected_planet.selected = False
                    self.selected_planet = None
                elif self.selected_planet is not None:
                    self.selected_planet.send_ships(self, self.active_planet, self.power)
                    self.selected_planet.selected = False
                    self.selected_planet = None

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

    def change_power(self):
        if self.power < 1:
            self.power += 0.25
        else:
            self.power = 0.25
        self.power_button.update('{0:.0f}%'.format(self.power * 100))

    def redraw(self, screen):
        rects = []
        rects += self.rect_exit_menu(screen)
        if not self.exit_menu_shown:
            self.menu_buttons.clear(self.screen, self.bg)
            self.statusBoxes.clear(self.screen, self.bg)
        rects += self.buttons.draw(self.screen)
        rects += self.draw(screen)
        rects.append(self.draw_info(screen))
        rects += self.ships.draw(screen)
        return rects

    def generate_mocked_planets(self, player, enemies):
        planets = []
        # for current player
        planets.append(Planet(1, 100, 100, randint(30, 60), player, self))
        planets.append(Planet(2, 400, 200, randint(30, 60), player, self))

        # for enemies
        planets.append(Planet(3, 720, 200, randint(30, 100), enemies[0], self))
        planets.append(Planet(3, 850, 600, randint(30, 100), enemies[1], self))

        return planets
