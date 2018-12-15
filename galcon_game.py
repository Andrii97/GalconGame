import pygame as pg
import pygame.display as disp
import pygame.event as pgevent
import pygame.freetype as pgfont
import pygame.time as pgtime

from galcon_view import GameView
from menu import Menu, StartMPMenu, JoinMPMenu, SettingsMenu, PreGameMenu
from models import Color


class GalconGame:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.user = User('User', Color.RED)
        pg.mixer.init()
        self.clock = pgtime.Clock()
        self.screen = disp.set_mode((w, h))
        disp.set_caption("Galcon-Client-Team-3")
        self.running = True
        self.mode = None

        self.startMPMenu = None
        self.joinMPMenu = None
        self.preGameMenu = None
        self.settingsMenu = None
        self.gameView = None
        
        # create the menu beforehand
        self.mainMenu = Menu(self.w, self.h)
        self.__createMainMenu__()
        self.show_main_menu()

    def run(self):

        while self.running:

            # check events
            for event in pgevent.get():
                if event.type == pg.KEYDOWN:
                    self.key_pressed(event)
                elif event.type == pg.MOUSEMOTION:
                    self.mouse_move(event)
                elif event.type == pg.MOUSEBUTTONDOWN:
                    self.mouse_down(event)
                elif event.type == pg.MOUSEBUTTONUP:
                    self.mouse_up(event)
                elif event.type == pg.QUIT:
                    self.running = False
            if not self.running:
                break
            # step timer
            self.timer_fired()
            self.redraw()
            self.clock.tick(30)

    def __createMainMenu__(self):
        self.mainMenu = Menu(self.w, self.h)
        self.mainMenu.star_bg()
        but_w = 300

        self.mainMenu.add_label("WELCOME TO GALCON", self.w // 2, 140, font=pgfont.SysFont('Tahoma', 28))
        self.mainMenu.add_status_box('name', self.user.name, self.w // 2, 180, font=pgfont.SysFont('Tahoma', 32),
                                     text_color=self.user.color)
        self.mainMenu.add_button("START MULTIPLAYER", pg.Rect((self.w - but_w) // 2, 250, but_w, 50), 
                                 self.show_start_mp_menu)
        self.mainMenu.add_button("JOIN MULTIPLAYER", pg.Rect((self.w - but_w) // 2, 310, but_w, 50), 
                                 self.show_join_mp_menu)
        self.mainMenu.add_button("SETTINGS", pg.Rect((self.w - but_w) // 2, 370, but_w, 50), 
                                 self.show_settings)
        self.mainMenu.add_button("QUIT", pg.Rect((self.w - but_w) // 2, 430, but_w, 50), self.quit_game)

    def show_main_menu(self):
        self.mainMenu.pressed = None
        self.mode = self.mainMenu
        self.screen.blit(self.mode.bg, (0, 0))
        self.mode.update_status_box('name', self.user.name, self.user.color)
        disp.update()

        if not pg.mixer.music.get_busy():
            self.play_music()

    def quit_game(self):
        self.running = False

    def show_settings(self):
        self.settingsMenu = SettingsMenu(self.w, self.h, self.user, self.show_main_menu)
        self.mode = self.settingsMenu
        self.screen.blit(self.mode.bg, (0, 0))
        disp.update()

    def show_start_mp_menu(self):
        self.startMPMenu = StartMPMenu(self.w, self.h, self.show_game_view, self.show_main_menu, self.user)
        self.startMPMenu.pressed = None
        self.mode = self.startMPMenu
        self.startMPMenu.update_status_box('name', self.user.name, self.user.color)
        self.screen.blit(self.mode.bg, (0, 0))
        disp.update()

    def show_join_mp_menu(self):
        self.joinMPMenu = JoinMPMenu(self.w, self.h, self.show_main_menu, self.user)
        self.joinMPMenu.pressed = None
        self.mode = self.joinMPMenu
        self.joinMPMenu.update_status_box('name', self.user.name, self.user.color)
        self.screen.blit(self.mode.bg, (0, 0))
        disp.update()

    def start_pre_game(self):
        self.preGameMenu = PreGameMenu(self.w, self.h)
        self.mode = self.preGameMenu
        self.screen.blit(self.mode.bg, (0, 0))
        disp.update()
    
    def show_game_view(self):
        self.gameView = GameView(self.w, self.h, self.screen, self.user, self.show_main_menu)
        self.gameView.accept_planets(
            self.gameView.generate_mocked_planets(
                self.user, [User("Bot1", Color.BLUE), User("Bot2", Color.GREEN)]
            )
        )
        self.mode = self.gameView
        self.screen.blit(self.mode.bg, (0, 0))
        self.gameView.draw(self.screen)
        disp.update()

    def play_music(self):
        pg.mixer.music.load('media/bgm.mp3')
        pg.mixer.music.play(-1)

    def timer_fired(self):
        self.mode.timer_fired()

    def mouse_move(self, event):
        self.mode.mouse_move(event)

    def mouse_down(self, event):
        self.mode.mouse_down(event)

    def mouse_up(self, event):
        self.mode.mouse_up(event)

    def key_pressed(self, event):
        self.mode.key_pressed(event)

    def redraw(self):
        rects = self.mode.redraw(self.screen)
        disp.update(rects)


class User:
    def __init__(self, name, color):
        self.name = name
        self.color = color


def main():
    game = GalconGame(1024, 768)
    game.run()


if __name__ == '__main__':
    main()
