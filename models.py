import pygame as pg
import pygame.freetype as pgfont
import pygame.gfxdraw as gfx
from random import randint


class Color:
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    WHITE = (255, 255, 255)
    YELLOW = (255, 255, 0)
    ORANGE = (255, 165, 0)
    PURPLE = (128, 0, 128)
    MIDNIGHT_EXPRESS = (0, 0, 63)
    LIGHT_SLATE_BLUE = (127, 127, 255)
    DARK_GREEN = (0, 127, 0)  # it is not real dark

    @staticmethod
    def colors():
        return [Color.RED, Color.GREEN, Color.BLUE, Color.YELLOW, Color.ORANGE, Color.PURPLE]
    
    @staticmethod
    def random(ignore=None):
        colors = Color.colors()
        if ignore is not None:
            for x in ignore:
                colors.remove(x)
        return colors[randint(0, len(colors) - 1)]
        


class Planet(pg.sprite.Sprite):
    planet_red_img = pg.image.load('materials/planet_red.png')
    planet_green_img = pg.image.load('materials/planet_green.png')
    planet_blue_img = pg.image.load('materials/planet_blue.png')
    planet_orange_img = pg.image.load('materials/planet_orange.png')
    planet_yellow_img = pg.image.load('materials/planet_yellow.png')
    planet_purple_img = pg.image.load('materials/planet_purple.png')

    planets = {
        Color.RED: planet_red_img,
        Color.GREEN: planet_green_img,
        Color.BLUE: planet_blue_img,
        Color.ORANGE: planet_orange_img,
        Color.YELLOW: planet_yellow_img,
        Color.PURPLE: planet_purple_img,
    }

    def __init__(self, id, x, y, radius, owner):
        pg.sprite.Sprite.__init__(self)
        self.id = id
        self.pos_x = x
        self.pos_y = y
        self.radius = radius
        self.owner = owner
        self.units = PlanetUnits(self, round(radius / 2))
        self.sprites = pg.sprite.RenderUpdates()
        self.sprites.add(self.units)
        # load sprite for image,
        self.img = self.__load_image_for_color__()

        self.rect = self.img.get_rect()
        self.rect.center = (x, y)

    def draw(self, screen):
        screen.blit(self.img, self.rect)
        # self.sprites.clear(screen, bg)
        rects = []
        rects += self.sprites.draw(screen)
        return rects

    def __load_image_for_color__(self):
        img = self.planets.get(self.owner.color, self.planet_blue_img)
        img = pg.transform.scale(img, (self.radius * 2, self.radius * 2))
        return img


class PlanetUnits(pg.sprite.DirtySprite):
    AURA = 5  # width of aura around planet
    ALPHA = 15

    def __init__(self, planet, count=None):
        super().__init__()
        self.planet = planet
        self.count = count
        self.generation_coef = 0.001
        self.__createImage__()

    def update(self):
        self.count += self.planet.radius * self.generation_coef
        self.__createImage__()

    def __createImage__(self):
        if self.planet.owner.color is None:
            color = Color.WHITE  # neutral planet
        else:
            color = self.planet.owner.color

        count = "" if self.count is None else str(round(self.count))

        radius = self.planet.radius + PlanetUnits.AURA
        w = h = radius * 2 + 1
        self.image = pg.Surface((w, h), flags=pg.SRCALPHA)

        gfx.aacircle(self.image, radius, radius, radius, color)
        self.font = pgfont.SysFont("Comic Sans MS", self.planet.radius)
        self.text, rt = self.font.render(count, Color.WHITE)
        self.image.blit(self.text, (radius - self.text.get_width() // 2,
                                    radius - self.text.get_height() // 2))

    @property
    def rect(self):
        rect = self.planet.rect.copy()
        rect.centerx -= PlanetUnits.AURA
        rect.centery -= PlanetUnits.AURA
        rect.inflate(PlanetUnits.AURA * 2, PlanetUnits.AURA * 2)
        return rect
