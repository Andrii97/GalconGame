import os
import sys
from galcon_view import GalconView
from menu import Menu, StartMPMenu, JoinMPMenu, SettingsMenu, PreGameMenu
from galcon_network import GalconNetwork
import pygame as pg
import pygame.display as disp
import pygame.event as pgevent
import pygame.time as pgtime
import pygame.freetype as pgfont



class GalconGame():
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.user = User('User', (255, 0, 0))
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
        
        # create the menu beforehand
        self.mainMenu = Menu(self.w, self.h)
        self.__createMainMenu__()
        self.showMainMenu()

    def run(self):

        while self.running:

            # check events
            for event in pgevent.get():
                if event.type == pg.KEYDOWN:
                    self.keyPressed(event)
                elif event.type == pg.MOUSEMOTION:
                    self.mouseMove(event)
                elif event.type == pg.MOUSEBUTTONDOWN:
                    self.mouseDown(event)
                elif event.type == pg.MOUSEBUTTONUP:
                    self.mouseUp(event)
                elif event.type == pg.QUIT:
                    self.running = False
            if not self.running: break
            # step timer
            self.timerFired()
            self.redraw()
            self.clock.tick(30)

    def __createMainMenu__(self):
        self.mainMenu = Menu(self.w, self.h)
        self.mainMenu.starBG()
        butW = 300

        self.mainMenu.addLabel("GALCON", self.w // 2, 100,
                               font=pgfont.SysFont('Tahoma', 32))
        self.mainMenu.addButton("START MULTIPLAYER", pg.Rect((self.w - butW) // 2, 250,
                                                butW, 50),
                                self.showStartMPMenu)
        self.mainMenu.addButton("JOIN MULTIPLAYER",
                                pg.Rect((self.w - butW) // 2, 310, butW, 50),
                                self.showJoinMPMenu)
        self.mainMenu.addButton("SETTINGS",
                                pg.Rect((self.w - butW) // 2, 370, butW, 50),
                                self.showSettings)
        self.mainMenu.addButton("QUIT",
                                pg.Rect((self.w - butW) // 2, 430, butW, 50),
                                self.quitGame)

    def showMainMenu(self):
        self.mainMenu.pressed = None
        self.mode = self.mainMenu
        self.screen.blit(self.mode.bg, (0, 0))
        disp.update()

        if not pg.mixer.music.get_busy():
            self.playMusic()

    def quitGame(self):
        self.running = False

    def showSettings(self):
        self.settingsMenu = SettingsMenu(self.w, self.h, self.user, self.showMainMenu)
        self.settingsMenu.pressed = None
        self.mode = self.settingsMenu
        self.screen.blit(self.mode.bg, (0, 0))
        disp.update()

    def showStartMPMenu(self):
        self.startMPMenu = StartMPMenu(self.w, self.h, self.startPreGame, self.showMainMenu)
        self.startMPMenu.pressed = None
        self.mode = self.startMPMenu
        self.screen.blit(self.mode.bg, (0, 0))
        disp.update()

    def showJoinMPMenu(self):
        self.joinMPMenu = JoinMPMenu(self.w, self.h,self.showMainMenu)
        self.joinMPMenu.pressed = None
        self.mode = self.joinMPMenu
        self.screen.blit(self.mode.bg, (0, 0))
        disp.update()

    def startPreGame(self):
        self.preGameMenu = PreGameMenu(self.w, self.h)
        self.mode = self.preGameMenu
        self.screen.blit(self.mode.bg, (0, 0))
        disp.update()

    def playMusic(self):
        pg.mixer.music.load('media/bgm.mp3')
        pg.mixer.music.play(-1)

    def timerFired(self):
        self.mode.timerFired()

    def mouseMove(self, event):
        self.mode.mouseMove(event)

    def mouseDown(self, event):
        self.mode.mouseDown(event)

    def mouseUp(self, event):
        self.mode.mouseUp(event)

    def keyPressed(self, event):
        self.mode.keyPressed(event)

    def redraw(self):
        rects = self.mode.redraw(self.screen)
        disp.update(rects)


class User():
    def __init__(self, name, color):
        self.name = name
        self.color = color

def main():
    game = GalconGame(1024, 768)
    game.run()


if __name__ == '__main__':
    main()
