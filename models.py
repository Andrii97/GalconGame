import pygame as pg


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
    DARK_GREEN = (0, 127, 0) # it is not real dark


class Planet(pg.sprite.Sprite):
    planet_red_img = pg.image.load('materials/planet_red.png')
    planet_green_img = pg.image.load('materials/planet_green.png')
    planet_blue_img = pg.image.load('materials/planet_blue.png')

    planets = {
        Color.RED: planet_red_img,
        Color.GREEN: planet_green_img,
        Color.BLUE: planet_blue_img
    }

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
        img = self.planets.get(self.owner.color, self.planet_blue_img)
        img = pg.transform.scale(img, (self.radius * 2, self.radius * 2))
        return img