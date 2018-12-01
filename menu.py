import sys
import pygame as pg
import pygame.display as disp
import pygame.event as pgevent
import pygame.gfxdraw as gfx
import pygame.time as pgtime
import pygame.sprite as sp
import pygame.surfarray as sfa
import pygame.transform as tf
import pygame.freetype as pgfont
import numpy as np
from random import *
import math
MAX_PLAYERS, MIN_PLAYERS = 3, 2

class Menu():

    pgfont.init()
    LABELFONT = pgfont.SysFont('Tahoma', 16)
    FONTCOLOR = (0, 255, 0)

    def __init__(self, w, h):
        super().__init__()
        self.w, self.h = w, h
        self.buttons = sp.RenderUpdates()
        self.textBoxDict = dict()
        self.statusBoxDict = dict()
        self.statusBoxes = sp.RenderUpdates()
        self.pressed = None
        self.textBoxActive = None
        self.bg = pg.Surface((w, h))
        self.bg.fill((0, 0, 0))
        

    def starBG(self):
        self.bg = self.genStarBG(self.w, self.h)

    def genStarBG(self, w, h, stars=None, starRMin=3, starRMax=20, starRVar=0.5):
        if stars is None:
            stars = int(w * h / 10 ** 4)
        MARGIN = 5
        bg = pg.Surface((w, h))
        for s in range(stars):
            x = randint(MARGIN, w - MARGIN)
            y = randint(MARGIN, h - MARGIN)
            r = int(starRMin + expovariate(starRVar))
            if r > starRMax: r = starRMax
            bg.blit(self.whiteStar(r), (x, y))
        return bg

    def whiteStar(self, r):
        a = np.full((3, 3, 3), 0, dtype=int)
        a[1][1] = (255, 255, 255)
        return tf.smoothscale(sfa.make_surface(a), (r, r))


    def addButton(self, *args):
        self.buttons.add(Button(*args))

    def addTextBox(self, name, *args, **kwargs):
        newBox = TextBox(*args, **kwargs)
        self.textBoxDict[name] = newBox
        self.buttons.add(newBox)

    def getTextBox(self, name):
        return self.textBoxDict[name].text

    def addLabel(self, text, x, y, font=None, anchor=None):
        if font is None: font = Menu.LABELFONT
        textImage, rt = font.render(text, Menu.FONTCOLOR)
        if anchor == 'N':
            topLeft = x - rt.width // 2, y
        elif anchor == 'W':
            topLeft = x ,y - rt.height // 2
        elif anchor == 'NW':
            topLeft = x, y
        else: # default to center
            topLeft = (x - rt.width // 2,
                       y - rt.height // 2)
        self.bg.blit(textImage, topLeft)

    def addImage(self, img, loc, dims=None):
        if dims is None:
            self.bg.blit(img, loc)
        else:
            dims = tuple(map(int, dims))
            self.bg.blit(tf.scale(img, dims), loc)

    def addMultilineLabel(self, *args, **kwargs):
        mlLabel = MultilineLabel(*args, **kwargs)
        self.bg.blit(mlLabel.image, mlLabel.rect)

    def addStatusBox(self, name, *args, **kwargs):
        newBox = StatusBox(*args, **kwargs)
        self.statusBoxDict[name] = newBox
        self.statusBoxes.add(newBox)

    def updateStatusBox(self, name, *args, **kwargs):
        self.statusBoxDict[name].updateText(*args, **kwargs)

    def timerFired(self):
        pass

    def mouseMove(self, event):
        if self.pressed: return
        for but in self.buttons:
            if but.containsPt(event.pos):
                but.mouseOver()
            else:
                but.unMouseOver()

    def mouseDown(self, event):
        if self.textBoxActive: self.textBoxActive.deactivate()
        if event.button == 1:
            for but in self.buttons:
                if but.containsPt(event.pos):
                    if isinstance(but, Button):
                        self.pressed = but
                        but.press()
                    elif isinstance(but, TextBox):
                        self.textBoxActive = but
                        but.activate()

    def mouseUp(self, event):
        if self.pressed:
            if self.pressed.containsPt(event.pos):
                self.pressed.release()
            else:
                self.pressed.unpress()
                self.pressed = None

    def keyPressed(self, event):
        if self.textBoxActive:
            if event.key == 8: # backspace
                self.textBoxActive.removeText()
            elif event.key == 13:
                self.textBoxActive.enterFn()
            else:
                self.textBoxActive.addText(event.unicode)

    def redraw(self, screen):
        self.statusBoxes.clear(screen, self.bg)
        rects = self.buttons.draw(screen)
        rects += self.statusBoxes.draw(screen)
        return rects

class Button(sp.DirtySprite):

    COLOR = (0, 255, 0)
    COLORO = (0, 63, 0)
    COLORP = (0, 127, 0)

    pgfont.init()
    FONT = pgfont.SysFont('Tahoma', 16)

    def __init__(self, text, rect, fn, args=tuple()):
        super().__init__()
        self.text = text
        self.rect = rect
        self.fn = fn
        self.args = args
        self.imageBase = pg.Surface((rect.width, rect.height))
        self.imageMouseOver = pg.Surface((rect.width, rect.height))
        self.imageMousePress = pg.Surface((rect.width, rect.height))
        self.image = self.imageBase
        self.__createImages__()

        self.pressed = False

    def __createImages__(self):
        textImage, r  = Button.FONT.render(self.text, Button.COLOR)
        textTopLeft = ((self.rect.width - textImage.get_width()) // 2,
                       (self.rect.height - textImage.get_height()) // 2)
        imgRect = self.image.get_rect()
        gfx.rectangle(self.imageBase, imgRect, Button.COLOR)
        self.imageBase.blit(textImage, textTopLeft)
        self.imageMouseOver.fill(Button.COLORO)
        gfx.rectangle(self.imageMouseOver, imgRect, Button.COLOR)
        self.imageMouseOver.blit(textImage, textTopLeft)
        self.imageMousePress.fill(Button.COLORP)
        gfx.rectangle(self.imageMousePress, imgRect, Button.COLOR)
        self.imageMousePress.blit(textImage, textTopLeft)

    def containsPt(self, pt):
        return self.rect.collidepoint(pt)

    def mouseOver(self):
        self.image = self.imageMouseOver

    def unMouseOver(self):
        self.image = self.imageBase

    def press(self):
        self.image = self.imageMousePress
        self.pressed = True

    def unpress(self):
        self.image = self.imageBase
        self.pressed = False

    def release(self):
        self.image = self.imageBase
        if self.pressed: self.fn(*self.args)


class TextBox(sp.DirtySprite):

    COLOR = (0, 0, 255)
    COLORO = (0, 0, 63)
    COLORP = (127, 127, 255)

    pgfont.init()
    FONT = pgfont.SysFont('Tahoma', 20)

    def __init__(self, rect, enterFn=lambda x: None, defaultText=""):
        super().__init__()
        self.text = defaultText
        self.rect = rect
        self.enterFn = enterFn
        self.imageBase = pg.Surface((rect.width, rect.height))
        self.imageMouseOver = pg.Surface((rect.width, rect.height))
        self.imageMousePress = pg.Surface((rect.width, rect.height))
        self.image = self.imageBase
        self.imgRect = self.image.get_rect()
        self.__typingImages__()
        self.__staticImages__()
        self.active = False

    def __staticImages__(self):
        gfx.rectangle(self.imageBase, self.imgRect, TextBox.COLOR)
        self.imageMouseOver.fill(TextBox.COLORO)
        gfx.rectangle(self.imageMouseOver, self.imgRect, TextBox.COLOR)
        if self.text:
            staticTextImage, r = TextBox.FONT.render(self.text, TextBox.COLOR)
            self.imageBase.blit(staticTextImage, self.textTopLeft)
            self.imageMouseOver.blit(staticTextImage, self.textTopLeft)

    def __typingImages__(self):
        self.imageMousePress.fill((0, 0, 0))
        gfx.rectangle(self.imageMousePress, self.imgRect, TextBox.COLORP)
        if self.text:
            textImage, r = TextBox.FONT.render(self.text, TextBox.COLORP)
            self.textTopLeft = ((self.rect.width - textImage.get_width()) // 2,
                           (self.rect.height - textImage.get_height()) // 2)
            self.imageMousePress.blit(textImage, self.textTopLeft)
        self.image = self.imageMousePress

    def containsPt(self, pt):
        return self.rect.collidepoint(pt)

    def mouseOver(self):
        if not self.active: self.image = self.imageMouseOver

    def unMouseOver(self):
        if not self.active: self.image = self.imageBase

    def activate(self):
        self.__typingImages__()
        self.image = self.imageMousePress
        self.active = True

    def addText(self, c):
        self.text += c
        self.__typingImages__()

    def removeText(self):
        if len(self.text) > 0:
            self.text = self.text[:-1]
            self.__typingImages__()

    def clearText(self):
        self.text = ""
        self.__typingImages__()

    def deactivate(self):
        self.__staticImages__()
        self.image = self.imageBase
        self.active = False

class StatusBox(sp.DirtySprite):

    COLOR = (0, 255, 0)
    pgfont.init()
    FONT = pgfont.SysFont('Tahoma', 16)

    def __init__(self, text, x, y, anchor=None, font=None, textColor=None):
        super().__init__()
        self.text = text
        self.x, self.y = x, y
        self.anchor = anchor
        if font is None: self.font = StatusBox.FONT
        else: self.font = font
        if textColor is None: self.textColor = StatusBox.COLOR
        else: self.textColor = textColor
        self.__createImage__()

    def __createImage__(self):
        self.image, r = self.font.render(self.text, self.textColor)
        if self.anchor == 'N':
            topLeft = self.x - self.image.get_width() // 2, self.y
        elif self.anchor == 'W':
            topLeft = self.x , self.y - self.image.get_height() // 2
        elif self.anchor == 'NW':
            topLeft = self.x, self.y
        else: # default to center
            topLeft = (self.x - self.image.get_width() // 2,
                       self.y - self.image.get_height() // 2)
        self.rect = pg.Rect(*topLeft, self.image.get_width(),
                            self.image.get_height())

    def updateText(self, text=None, color=None):
        if text is not None:
            self.text = text
        if color is not None:
            self.textColor = color
        if not (color is None and text is None):
            self.__createImage__()

class MultilineLabel(sp.Sprite):

    COLOR = (0, 255, 0)
    pgfont.init()
    FONT = pgfont.SysFont('Tahoma', 20)
    PARA_MARGIN = 15
    LINE_MARGIN = 5

    def __init__(self, text, x, y, maxW):
        super().__init__()
        self.text = text
        self.x, self.y = x, y
        self.maxW = maxW
        self.__createImage__()

    def __createImage__(self):
        paraList = []
        self.h = 0
        for paragraph in self.text.splitlines():
            sf, h = self.__createParagraphImage__(paragraph)
            paraList.append((sf, h))
            self.h += h + MultilineLabel.PARA_MARGIN
        self.image = pg.Surface((self.maxW, self.h))
        currY = 0
        for sf, h in paraList:
            self.image.blit(sf, (0, currY))
            currY += h + MultilineLabel.PARA_MARGIN

    def __createParagraphImage__(self, text):
        wordList = text.split()
        lineList = []
        lineSfList = []
        h = 0
        nextLine = wordList.pop(0)
        while nextLine:
            currLine, nextLine = nextLine, ""
            while MultilineLabel.FONT.get_rect(currLine).width < self.maxW:
                if not wordList: break
                currLine += " " + wordList.pop(0)
            else:
                currLine, nextLine = currLine.rsplit(" ", 1)
            lineList.append(currLine)
        for l in lineList:
            sf, r = MultilineLabel.FONT.render(l, MultilineLabel.COLOR)
            lineSfList.append((sf, r))
            h += r.height + MultilineLabel.LINE_MARGIN
        image = pg.Surface((self.maxW, h))
        currY = 0
        for sf, r in lineSfList:
            image.blit(sf, (0, currY))
            currY += r.height + MultilineLabel.LINE_MARGIN
        return image, h

    @property
    def rect(self):
        return pg.Rect(self.x, self.y, self.maxW, self.h)



class SettingsMenu(Menu):
    def __init__(self, w, h, user, mainMenu):
        super().__init__(w, h)
        self.starBG()
        self.mainMenu = mainMenu
        butW = 300
        self.addLabel("Change Name:", w // 2, 230)
        self.addTextBox("Name", pg.Rect((w - butW) // 2, 250, butW, 70), defaultText=user.name)
        self.addLabel("Change Color:" ,w // 2, 350)
        self.addTextBox("Color", pg.Rect((w - butW) // 2, 370, butW, 70))
        self.addStatusBox("status", "", w // 2, 480)
        self.addButton("SAVE", pg.Rect((w - butW) // 2, 500, butW, 50), self.validate)
        self.addButton("BACK", pg.Rect((w - butW) // 2, 560, butW, 50), mainMenu)
        

    def validate(self):
        #Check values
        self.mainMenu()


class StartMPMenu(Menu):

    def __init__(self, w, h, preGameMenu, mainMenu):
        super().__init__(w, h)
        self.starBG()
        self.preGameMenu = preGameMenu
        butW = 300
        self.addLabel("Enter your own IP address:", w // 2, 230)
        self.addTextBox("IP", pg.Rect((w - butW) // 2, 250, butW, 70))
        self.addLabel("Number of players (%d-%d):" % (MIN_PLAYERS, MAX_PLAYERS),
                      w // 2, 350)
        self.addTextBox("players", pg.Rect((w - butW) // 2, 370, butW, 70))
        self.addStatusBox("status", "", w // 2, 480)
        self.addButton("START", pg.Rect((w - butW) // 2, 500, butW, 50), self.validate)
        self.addButton("BACK", pg.Rect((w - butW) // 2, 560, butW, 50), mainMenu)
        self.numPlayers = 2

    def validate(self):
        #Check values
        self.preGameMenu()



class JoinMPMenu(Menu):

    def __init__(self, w, h, mainMenu):
        super().__init__(w, h)
        self.starBG()
        butW = 300
        self.addLabel("Enter the IP address to connect to:", w // 2, 225)
        self.addTextBox("IP", pg.Rect((w - butW) // 2, 250, butW, 100),
                        self.connectToServer)
        self.addStatusBox("status", "", w // 2, 400)
        self.addButton("CONNECT AND START", pg.Rect((w - butW) // 2,
                                                    440, butW, 50),
                       self.connectToServer)
        self.addButton("BACK", pg.Rect((w - butW) // 2, 500, butW, 50),
                       mainMenu)

    def connectToServer(self):
        self.updateStatusBox("status", "Trying to connect...")



class PreGameMenu(Menu):

    def __init__(self, w, h):
        super().__init__(w, h)
        self.addStatusBox("status", "", w // 2, 400)
        self.start()


    def start(self):
        self.updateStatusBox("status", "Waiting for other players...")

