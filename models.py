import math
from math import pi
from random import randint

import pygame as pg
import pygame.freetype as pgfont
import pygame.gfxdraw as gfx
import pygame.transform as tf


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
    BLACK = (0, 0, 0)

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
    SPAWN_TIME = 300
    SPAWN_CAP = 50

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

    def __init__(self, id, x, y, radius, owner, gameMap):
        pg.sprite.Sprite.__init__(self)
        self.map = gameMap
        self.id = id
        self.pos_x = x
        self.pos_y = y
        self.radius = radius
        self.spawnRate = radius ** 2 // 100
        self.spawnTimer = 0
        self.capped = False
        self.owner = owner
        self.selected = False
        self.units = PlanetUnits(self, round(radius / 2))
        self.sprites = pg.sprite.RenderUpdates()
        self.sprites.add(self.units)
        self.img = self.__load_image_for_color__()
        self.rect = self.img.get_rect()
        self.rect.center = self.loc

    @property
    def loc(self):
        return self.pos_x, self.pos_y

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

    def set_image(self):
        self.img = self.__load_image_for_color__()
        self.rect = self.img.get_rect()
        self.rect.center = self.loc

    def name(self, pName):
        if self.pName is None:
            self.pName = pName

    def closest_point(self, x, y):
        """Returns the closest point to pt on the planet."""
        angle = get_angle(*self.loc, x, y)
        return carte_plus_polar(*self.loc, self.radius, angle)

    def cap(self, new_owner):
        self.owner = new_owner
        self.capped = True
        self.spawnTimer = Planet.SPAWN_TIME
        self.set_image()

    def arrival(self, owner):
        if self.owner == owner:
            self.units.count += 1
        else:
            self.units.count -= 1
            if self.units.count < 0:
                self.cap(owner)
                self.units.count = 1

    def spawn_tick(self):
        if not self.capped or self.units >= Planet.SPAWN_CAP: return
        self.spawnTimer -= self.spawnRate
        if self.spawnTimer <= 0:
            self.units += 1
            self.spawnTimer = Planet.SPAWN_TIME

    def send_ships(self, game, destination_planet, power):

        # finds available locations around a planet to spawn the
        # ships in a circle around a planet
        BUFFER_SPACE = 1
        num_ships = int(self.units.count * power)

        # create a new group of ships
        cluster = Cluster(destination_planet, self.owner)
        game.clusterNames[cluster.name] = cluster

        # initial values
        start_angle = get_angle(*self.loc, *destination_planet.loc)
        spawn_dist = self.radius + Ship.RADIUS + BUFFER_SPACE
        ships_made = 0
        while ships_made < num_ships:
            angle_step = math.asin((Ship.RADIUS + BUFFER_SPACE) / (spawn_dist))
            curr_angle = start_angle
            while curr_angle < pi * 2:
                spawnPt = carte_plus_polar(*self.loc, spawn_dist, curr_angle)
                try_ship = Ship(spawnPt, self, destination_planet)
                collision = (pg.sprite.spritecollideany(try_ship, game.ships,
                                                        Ship.collided_ship) or
                             pg.sprite.spritecollideany(try_ship, game.planets,
                                                        Ship.collided_ship))
                if collision:
                    # failPoints.append(spawnPt)
                    del try_ship  # get rid of failed object
                else:
                    game.ships.add(try_ship)
                    cluster.add(try_ship)
                    ships_made += 1
                    self.units.count -= 1
                    if ships_made == num_ships: break
                curr_angle += 2 * angle_step

            spawn_dist += 2 * Ship.RADIUS + BUFFER_SPACE


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
        if self.planet.selected:
            gfx.aacircle(self.image, radius, radius, radius, color)
        else:
            gfx.aacircle(self.image, radius, radius, radius, Color.BLACK)
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


class Cluster(pg.sprite.RenderUpdates):
    INDEX = 0

    def __init__(self, name, owner=None, dest=None):
        super().__init__()
        self.name = name
        self.owner = owner
        self.dest = dest

    def __init__(self, dest, owner):
        super().__init__()
        # self.name = name
        self.owner = owner
        self.dest = dest
        self.name = Cluster.INDEX
        Cluster.INDEX += 1

    def move(self, ships, planets):

        def move_unit(unit, tryTurns):
            for dist in range(Ship.VELOCITY, 0, -1):
                for turn in tryTurns:
                    unit.try_move(dist, turn)
                    collide_planet = pg.sprite.spritecollideany(unit, planets,
                                                               pg.sprite.collide_circle)
                    if collide_planet is unit.destination_planet:
                        unit.destination_planet.arrival(self.owner)
                        unit.kill()
                        return
                    else:
                        pass
                        # move_unit(unit, filtertryTurns)
                        # return
                    if (len(pg.sprite.spritecollide(unit, ships, False,
                                                    Ship.collided_ship)) == 1 and
                            not collide_planet):
                        unit.do_move()
                        return
                    else:
                        unit.un_try_move()

        numTurns = int(Ship.MAX_TURN // Ship.TURN_ANGLE)
        turnList = [i * Ship.TURN_ANGLE for i in range(- numTurns, numTurns + 1)]
        turnList += [Ship.MAX_TURN, -Ship.MAX_TURN]

        for unit in self:
            # sorts the possible turns so that the ship tries to go forward
            # first
            tryTurns = sorted(turnList, key=lambda x:
            abs(x + normalise(unit.offset_angle)))
            move_unit(unit, tryTurns)

    def change_dest(self, dest):
        self.dest = dest
        for ship in self:
            ship.destination_planet = dest

    def game_package(self):
        ships = []
        for ship in self:
            ships.append((ship.loc, ship.angle))
        return self.owner, self.dest.pName, ships

    def check_arrival(self):
        for ship in self:
            if ship.arrive():
                ship.destination_planet.arrival(self.owner)
                ship.kill()


class Ship(pg.sprite.DirtySprite):
    RADIUS = 6
    BACK_ANGLE = pi * 3 / 4
    MARGIN = 0
    VELOCITY = 3
    MAX_TURN = 0.9 * pi
    TURN_ANGLE = pi / 6

    def __init__(self, color, pt, angle, *groups):
        super().__init__(*groups)

        self.color = color
        self.x, self.y = pt
        self.angle = angle

        # create image
        self.h = self.w = Ship.RADIUS * 2
        self.imageO = pg.Surface((self.w, self.h), flags=pg.SRCALPHA)
        self.__createImage__()
        self.image = self.imageO
        self.__rotateImage__(angle)

    def __init__(self, pt, start_planet, destination_planet, *groups):
        super().__init__(*groups)

        self.color = start_planet.owner.color
        self.owner = start_planet.owner
        self.x, self.y = pt
        self.start_planet = start_planet
        self.destination_planet = destination_planet

        # create image
        self.h = self.w = Ship.RADIUS * 2
        self.angle = self.angle_to_destination
        self.imageO = pg.Surface((self.w, self.h), flags=pg.SRCALPHA)
        self.__createImage__()
        self.image = self.imageO
        self.__rotateImage__(self.angle)

        # for collision detection purposes
        self.oldX, self.oldY = 0, 0
        self.currTurn = 0

    @property
    def loc(self):
        return self.x, self.y

    @property
    def radius(self):
        return Ship.RADIUS

    def __createImage__(self):
        self.imageO.fill((0, 0, 0, 0))
        x1, y1 = map(lambda x: int(round(x)),
                     carte_plus_polar(Ship.RADIUS, Ship.RADIUS,
                                      Ship.RADIUS, Ship.BACK_ANGLE))
        x2, y2 = map(lambda x: int(round(x)),
                     carte_plus_polar(Ship.RADIUS, Ship.RADIUS,
                                      Ship.RADIUS, - Ship.BACK_ANGLE))
        x3, y3 = 2 * Ship.RADIUS, Ship.RADIUS
        gfx.aatrigon(self.imageO, x1, y1, x2, y2, x3, y3, self.color)

    def __rotateImage__(self, turn):
        self.image = tf.rotate(self.imageO, -math.degrees(turn))

    @property
    def rect(self):
        return pg.Rect(self.x - Ship.RADIUS, self.y - Ship.RADIUS,
                       Ship.RADIUS * 2, Ship.RADIUS * 2)

    def collided_ship(self, other):
        # only for other ships!
        x0, y0 = self.loc
        x1, y1 = other.loc
        return ((x1 - x0) ** 2 + (y1 - y0) ** 2) < (2 * Ship.RADIUS) ** 2

    def containsPt(self, pt):
        return norm(self.loc, pt) < Ship.RADIUS

    def pts(self, i=0):
        pt1 = carte_plus_polar(*self.loc, Ship.RADIUS, self.angle)
        pt2 = carte_plus_polar(*self.loc,
                               Ship.RADIUS, self.angle + Ship.BACK_ANGLE)
        pt3 = carte_plus_polar(*self.loc,
                               Ship.RADIUS, self.angle - Ship.BACK_ANGLE)
        pts = [pt1, pt2, pt3]
        if i == 0:
            return pts
        else:
            return pts[i - 1]

    @property
    def angle_to_destination(self):
        return get_angle(*self.loc, *self.destination_planet.loc)

    @property
    def offset_angle(self):
        return self.angle - self.angle_to_destination

    # in the context of pathfinding, will need several parameters:
    # a var tracking the current angle wrt to destination angle
    # a var tracking destination angle
    # vars for trying to move

    def try_move(self, dist, turn):
        self.currTurn = turn
        self.oldX, self.oldY = self.x, self.y
        self.x, self.y = carte_plus_polar(self.x, self.y, dist, self.angle + turn)

    def un_try_move(self):
        self.x, self.y = self.oldX, self.oldY

    def do_move(self):
        dist, angle = to_polar(self.x - self.oldX, self.y - self.oldY)
        if dist != 0:
            if abs(angle - self.angle_to_destination) < Ship.TURN_ANGLE:
                # this gets rid of some wobbling
                angle = self.angle_to_destination
            self.angle = angle

    def arrive(self):
        return self.destination_planet.containsPt(self.pts(1))


def normalise(angle):
    return (angle + pi) % (2 * pi) - pi


def to_polar(x, y):
    """Converts to polar form."""
    if x == 0 and y == 0:
        return 0, 0
    r = math.sqrt(x ** 2 + y ** 2)
    arg = (- pi / 2 if x == 0 else math.atan(y / x))
    if x < 0 and y <= 0:
        return r, arg - pi
    elif y < 0 <= x or (x > 0 and y >= 0):
        return r, arg
    elif x <= 0 < y:
        return r, arg + pi


def to_carte(r, arg):
    """Converts to cartesian form."""
    x = r * math.cos(arg)
    y = r * math.sin(arg)
    return x, y


def get_angle(x0, y0, x1, y1):
    """Returns angle of pt1 from pt0."""
    d, angle = to_polar(x1 - x0, y1 - y0)
    return angle


def carte_plus_polar(x0, y0, dr, darg):
    """Adds a polar tuple to a cartesian tuple."""
    dx, dy = to_carte(dr, darg)
    return x0 + dx, y0 + dy


def norm(pt1, pt2):
    x1, y1 = pt1
    x2, y2 = pt2
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
