import unittest
from models import Color, Planet, Ship
from galcon_game import User
from galcon_view import GameView


class TestColor(unittest.TestCase):

    def test_color_ignore(self):
        color = Color.random(ignore=[Color.RED])
        self.assertTrue(color != Color.RED)

    def test_colors_ignore(self):
        color = Color.random(ignore=[Color.RED, Color. BLUE, Color.GREEN, Color.ORANGE, Color.YELLOW])
        self.assertTrue(color == Color.PURPLE)


class TestPlanet(unittest.TestCase):

    def test_planet_creation(self):
        user = User('user', Color.RED)
        planet = Planet(1, 25, 25, 20, user, None)
        self.assertTrue(planet.units is not None)
        self.assertEqual(planet.spawnRate, 4)
        self.assertEqual(planet.owner, user)
        self.assertEqual(planet.capped, False)
        self.assertNotEqual(planet.img, None)
        self.assertNotEqual(planet.rect, None)

    def test_planet_cap(self):
        user1 = User('user', Color.RED)
        planet = Planet(1, 25, 25, 20, user1, None)
        user2 = User('user', Color.BLUE)
        planet.cap(user2)
        self.assertNotEqual(planet.owner, user1)
        self.assertEqual(planet.owner, user2)

    def test_planet_owner_ship_arrival(self):
        user = User('user', Color.RED)
        planet = Planet(1, 25, 25, 20, user, None)
        units_count = planet.units.count
        planet.arrival(user)
        self.assertEqual(planet.units.count, units_count + 1)
        self.assertEqual(planet.owner, user)

    def test_planet_enemy_ship_arrival(self):
        user = User('user', Color.RED)
        planet = Planet(1, 25, 25, 20, user, None)
        user2 = User('user2', Color.BLUE)
        units_count = planet.units.count
        planet.arrival(user2)
        self.assertEqual(planet.units.count, units_count - 1)
        self.assertEqual(planet.owner, user)


    def test_planet_last_ship_to_cap_arrival(self):
        user = User('user', Color.RED)
        planet = Planet(1, 25, 25, 1, user, None)
        user2 = User('user2', Color.BLUE)
        planet.arrival(user2)
        self.assertEqual(planet.owner, user2)
        self.assertEqual(planet.units.count, 1)

    def test_planet_units_genetation(self):
        user = User('user', Color.RED)
        planet = Planet(1, 25, 25, 2, user, None)
        planet.units.update()
        self.assertEqual(planet.units.count, 1.002)


class TestShip(unittest.TestCase):

    def test_ship_creation(self):
        user = User('user', Color.RED)
        start_planet = Planet(1, 25, 25, 2, user, None)
        destination_planet = Planet(1, 25, 25, 2, user, None)
        ship = Ship(1, start_planet, destination_planet)
        self.assertEqual(ship.owner, user)
        self.assertEqual(ship.color, Color.RED)


class TestGameView(unittest.TestCase):

    def setUp(self):
        user = User('user', Color.RED)
        global gameView
        gameView = GameView(20, 20, None, user, None)

    def test_creation_game_view(self):
        self.assertEqual(gameView.planets, [])
        self.assertEqual(gameView.active_planet, None)
        self.assertEqual(gameView.selected_planet, None)

    def test_creation_mocked_planets(self):
        enemy1 = User('user', Color.BLUE)
        enemy2 = User('user1', Color.PURPLE)
        planets = gameView.generate_mocked_planets(gameView.user, [enemy1, enemy2])
        self.assertEqual(len(planets), 4)
        self.assertEqual(planets[0].owner, gameView.user)
        self.assertEqual(planets[1].owner, gameView.user)
        self.assertEqual(planets[2].owner, enemy1)
        self.assertEqual(planets[3].owner, enemy2)
        self.assertEqual(len(gameView.planets), 0)

    def test_accepted_planets(self):
        enemy1 = User('user', Color.BLUE)
        enemy2 = User('user1', Color.PURPLE)
        planets = gameView.generate_mocked_planets(gameView.user, [enemy1, enemy2])
        gameView.accept_planets(planets)
        self.assertEqual(len(gameView.planets), 4)
        self.assertEqual(gameView.planets, planets)


if __name__ == '__main__':
    unittest.main()
