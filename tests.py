import unittest
from models import Color, Planet, Ship
from galcon_game import User
from galcon_view import GameView
from menu import SettingsMenu


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
        unit_count = planet.units.count
        planet.units.update()
        self.assertEqual(planet.units.count, unit_count + planet.radius * planet.units.generation_coef)

    def test_send_ships(self):
        planet = Planet(1, 100, 100, 20, User('user', Color.RED), None)
        destination_planet = Planet(2, 300, 300, 20, User('user', Color.RED), None)
        game = GameView(20, 20, None, User('user', Color.RED), None)
        num_ships = planet.units.count // 2
        units_start = planet.units.count
        planet.send_ships(game, destination_planet)
        self.assertEqual(planet.units.count, units_start - num_ships)


class TestShip(unittest.TestCase):

    def test_ship_creation(self):
        user = User('user', Color.RED)
        start_planet = Planet(1, 25, 25, 2, user, None)
        destination_planet = Planet(2, 100, 100, 2, user, None)
        ship = Ship((1, 1), start_planet, destination_planet)
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


class TestUserSettings(unittest.TestCase):
    def test_creation_settings_menu(self):
        user = User('user', Color.RED)
        settings_menu = SettingsMenu(10, 10, user, None)
        self.assertEqual(settings_menu.get_text_box('Name'), user.name)
        self.assertEqual(settings_menu.get_color_button().color_p, user.color)

    def test_user_name_minimum_length(self):
        user = User('user', Color.RED)
        settings_menu = SettingsMenu(10, 10, user, None)
        settings_menu.textBoxDict['Name'].text = 'us'
        settings_menu.validate()
        self.assertEqual(settings_menu.get_status_box('status').text, settings_menu.LESS_THAN_MIN_CHAR_ERROR_MSG)

    def test_user_name_maximum_length(self):
        user = User('user', Color.RED)
        settings_menu = SettingsMenu(10, 10, user, None)
        settings_menu.textBoxDict['Name'].text = 'qwertyuiopasdfghj'
        settings_menu.validate()
        self.assertEqual(settings_menu.get_status_box('status').text, settings_menu.MORE_THAN_MAX_CHAR_ERROR_MSG)

    def test_user_name_starts_with_digits(self):
        user = User('user', Color.RED)
        settings_menu = SettingsMenu(10, 10, user, None)
        settings_menu.textBoxDict['Name'].text = '1qwertt'
        settings_menu.validate()
        self.assertEqual(settings_menu.get_status_box('status').text, settings_menu.START_WITH_DIGIT_ERROR_MSG)

    def test_user_name_blank(self):
        user = User('user', Color.RED)
        settings_menu = SettingsMenu(10, 10, user, None)
        settings_menu.textBoxDict['Name'].text = ''
        settings_menu.validate()
        self.assertEqual(settings_menu.get_status_box('status').text, settings_menu.BLANK_ERROR_MSG)

    def test_user_name_forbidden_symbols_1(self):
        user = User('user', Color.RED)
        settings_menu = SettingsMenu(10, 10, user, None)
        settings_menu.textBoxDict['Name'].text = '.iuyd'
        settings_menu.validate()
        self.assertEqual(settings_menu.get_status_box('status').text, settings_menu.FORBIDDEN_SYMBOLS_ERROR_MSG)

    def test_user_name_forbidden_symbols_2(self):
        user = User('user', Color.RED)
        settings_menu = SettingsMenu(10, 10, user, None)
        settings_menu.textBoxDict['Name'].text = 'iuyd//'
        settings_menu.validate()
        self.assertEqual(settings_menu.get_status_box('status').text, settings_menu.FORBIDDEN_SYMBOLS_ERROR_MSG)

    def test_user_name_forbidden_symbols_3(self):
        user = User('user', Color.RED)
        settings_menu = SettingsMenu(10, 10, user, None)
        settings_menu.textBoxDict['Name'].text = '&&qwerty'
        settings_menu.validate()
        self.assertEqual(settings_menu.get_status_box('status').text, settings_menu.FORBIDDEN_SYMBOLS_ERROR_MSG)

    def test_user_name_forbidden_symbols_4(self):
        user = User('user', Color.RED)
        settings_menu = SettingsMenu(10, 10, user, None)
        settings_menu.textBoxDict['Name'].text = 'qwerty???'
        settings_menu.validate()
        self.assertEqual(settings_menu.get_status_box('status').text, settings_menu.FORBIDDEN_SYMBOLS_ERROR_MSG)

    def test_user_name_forbidden_symbols_5(self):
        user = User('user', Color.RED)
        settings_menu = SettingsMenu(10, 10, user, None)
        settings_menu.textBoxDict['Name'].text = 'qwerty(not)'
        settings_menu.validate()
        self.assertEqual(settings_menu.get_status_box('status').text, settings_menu.FORBIDDEN_SYMBOLS_ERROR_MSG)

    def test_user_name_forbidden_symbols_6(self):
        user = User('user', Color.RED)
        settings_menu = SettingsMenu(10, 10, user, None)
        settings_menu.textBoxDict['Name'].text = 'qwerty@mail.ru'
        settings_menu.validate()
        self.assertEqual(settings_menu.get_status_box('status').text, settings_menu.FORBIDDEN_SYMBOLS_ERROR_MSG)

    def test_user_settings_save(self):
        user = User('user', Color.RED)
        settings_menu = SettingsMenu(10, 10, user, lambda: print(''))
        settings_menu.textBoxDict['Name'].text = 'GalconPlayer'
        settings_menu.get_color_button().color_p = Color.PURPLE
        settings_menu.validate()
        self.assertEqual(settings_menu.user.name, settings_menu.get_text_box('Name'))


if __name__ == '__main__':
    unittest.main()
