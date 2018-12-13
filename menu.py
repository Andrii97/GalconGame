import pygame as pg
import pygame.gfxdraw as gfx
import pygame.sprite as sp
import pygame.surfarray as sfa
import pygame.transform as tf
import pygame.freetype as pgfont
import numpy as np
import re
from random import *
MAX_PLAYERS, MIN_PLAYERS = 3, 2


class Menu:

    pgfont.init()
    LABELFONT = pgfont.SysFont('Tahoma', 16)
    FONTCOLOR = (0, 255, 0)
    ERRORCOLOR = (255, 0, 0)

    def __init__(self, w, h):
        super().__init__()
        self.w, self.h = w, h
        self.buttons = sp.RenderUpdates()
        self.textBoxDict = dict()
        self.statusBoxDict = dict()
        self.statusBoxes = sp.RenderUpdates()
        self.error_text = ''
        self.pressed = None
        self.textBoxActive = None
        self.bg = pg.Surface((w, h))
        self.bg.fill((0, 0, 0))

    def star_bg(self):
        self.bg = self.gen_star_bg(self.w, self.h)

    def gen_star_bg(self, w, h, stars=None, star_min=3, star_max=20, star_var=0.5):
        if stars is None:
            stars = int(w * h / 10 ** 4)
        margin = 5
        bg = pg.Surface((w, h))
        for s in range(stars):
            x = randint(margin, w - margin)
            y = randint(margin, h - margin)
            r = int(star_min + expovariate(star_var))
            if r > star_max:
                r = star_max
            bg.blit(self.white_star(r), (x, y))
        return bg

    def white_star(self, r):
        a = np.full((3, 3, 3), 0, dtype=int)
        a[1][1] = (255, 255, 255)
        return tf.smoothscale(sfa.make_surface(a), (r, r))

    def add_button(self, *args):
        self.buttons.add(Button(*args))

    def add_color_button(self, *args):
        but = ColorButton(*args)
        if self.user.color == but.color_p:
            self.pressed = but
            but.press()

        self.buttons.add(but)

    def get_color_button(self):
        for but in self.buttons:
            if isinstance(but, ColorButton) and but.pressed:
                return but

    def add_text_box(self, name, *args, **kwargs):
        new_box = TextBox(*args, **kwargs)
        self.textBoxDict[name] = new_box
        self.buttons.add(new_box)

    def get_text_box(self, name):
        return self.textBoxDict[name].text

    def get_status_box(self, name):
        return self.statusBoxDict[name]

    def add_label(self, text, x, y, font=None, anchor=None):
        if font is None:
            font = Menu.LABELFONT
        text_image, rt = font.render(text, Menu.FONTCOLOR)
        if anchor == 'N':
            top_left = x - rt.width // 2, y
        elif anchor == 'W':
            top_left = x, y - rt.height // 2
        elif anchor == 'NW':
            top_left = x, y
        else:  # default to center
            top_left = (x - rt.width // 2, y - rt.height // 2)
        self.bg.blit(text_image, top_left)

    def add_image(self, img, loc, dims=None):
        if dims is None:
            self.bg.blit(img, loc)
        else:
            dims = tuple(map(int, dims))
            self.bg.blit(tf.scale(img, dims), loc)

    def add_multiline_label(self, *args, **kwargs):
        ml_label = MultilineLabel(*args, **kwargs)
        self.bg.blit(ml_label.image, ml_label.rect)

    def add_status_box(self, name, *args, **kwargs):
        new_box = StatusBox(*args, **kwargs)
        self.statusBoxDict[name] = new_box
        self.statusBoxes.add(new_box)

    def update_status_box(self, name, *args, **kwargs):
        self.statusBoxDict[name].update_text(*args, **kwargs)

    def timer_fired(self):
        pass

    def mouse_move(self, event):
        if self.pressed and not isinstance(self.pressed, ColorButton):
            return
        for but in self.buttons:
            if not isinstance(but, ColorButton):
                if but.contains_pt(event.pos):
                    but.mouse_over()
                else:
                    but.un_mouse_over()

    def mouse_down(self, event):
        if self.textBoxActive: 
            self.textBoxActive.deactivate()
        if event.button == 1:
            for but in self.buttons:
                if but.contains_pt(event.pos):
                    if isinstance(but, ColorButton):
                        if self.pressed:
                            self.pressed.unpress()
                        self.pressed = but
                        but.press()
                    elif isinstance(but, Button):
                        self.pressed = but
                        but.press()
                    elif isinstance(but, TextBox):
                        self.textBoxActive = but
                        but.activate()

    def mouse_up(self, event):
        if isinstance(self.pressed, ColorButton):
            return
        if self.pressed:
            if self.pressed.contains_pt(event.pos):
                self.pressed.release()
            else:
                self.pressed.unpress()
                self.pressed = None

    def key_pressed(self, event):
        if self.textBoxActive:
            if event.key == 8:  # backspace
                self.textBoxActive.remove_text()
            elif event.key == 13:
                self.textBoxActive.deactivate()
            else:
                self.textBoxActive.add_text(event.unicode)

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
        text_image, r = Button.FONT.render(self.text, Button.COLOR)
        text_top_left = ((self.rect.width - text_image.get_width()) // 2, 
                         (self.rect.height - text_image.get_height()) // 2)
        img_rect = self.image.get_rect()
        gfx.rectangle(self.imageBase, img_rect, Button.COLOR)
        self.imageBase.blit(text_image, text_top_left)
        self.imageMouseOver.fill(Button.COLORO)
        gfx.rectangle(self.imageMouseOver, img_rect, Button.COLOR)
        self.imageMouseOver.blit(text_image, text_top_left)
        self.imageMousePress.fill(Button.COLORP)
        gfx.rectangle(self.imageMousePress, img_rect, Button.COLOR)
        self.imageMousePress.blit(text_image, text_top_left)

    def contains_pt(self, pt):
        return self.rect.collidepoint(pt)

    def mouse_over(self):
        self.image = self.imageMouseOver

    def un_mouse_over(self):
        self.image = self.imageBase

    def press(self):
        self.image = self.imageMousePress
        self.pressed = True

    def unpress(self):
        self.image = self.imageBase
        self.pressed = False

    def release(self):
        self.image = self.imageBase
        if self.pressed: 
            self.fn(*self.args)


class ColorButton(sp.DirtySprite):

    pgfont.init()
    FONT = pgfont.SysFont('Tahoma', 16)

    def __init__(self, text, rect, color):
        super().__init__()
        self.text = text
        self.rect = rect
        self.color = tuple(component / 2 for component in color)
        self.imageBase = pg.Surface((rect.width, rect.height))
        self.color_p = color
        self.imageMouseOver = pg.Surface((rect.width, rect.height))
        self.imageMousePress = pg.Surface((rect.width, rect.height))
        self.image = self.imageBase
        self.__createImages__()

        self.pressed = False

    def __createImages__(self):
        self.imageBase.fill(self.color)
        self.imageMousePress.fill(self.color_p)

    def contains_pt(self, pt):
        return self.rect.collidepoint(pt)

    def press(self):
        self.image = self.imageMousePress
        self.pressed = True

    def unpress(self):
        self.image = self.imageBase
        self.pressed = False

    def release(self):
        self.image = self.imageBase
        self.pressed = False


class TextBox(sp.DirtySprite):

    COLOR = (0, 0, 255)
    COLORO = (0, 0, 63)
    COLORP = (127, 127, 255)

    pgfont.init()
    FONT = pgfont.SysFont('Tahoma', 20)

    def __init__(self, rect, enter_fn=lambda x: None, default_text=""):
        super().__init__()
        self.text = default_text
        self.rect = rect
        self.enterFn = enter_fn
        self.imageBase = pg.Surface((rect.width, rect.height))
        self.imageMouseOver = pg.Surface((rect.width, rect.height))
        self.imageMousePress = pg.Surface((rect.width, rect.height))
        self.image = self.imageBase
        self.imgRect = self.image.get_rect()
        self.__typingImages__()
        self.__staticImages__()
        self.active = False

    def __staticImages__(self):
        self.imageBase = pg.Surface((self.rect.width, self.rect.height))
        gfx.rectangle(self.imageBase, self.imgRect, TextBox.COLOR)
        self.imageMouseOver.fill(TextBox.COLORO)
        gfx.rectangle(self.imageMouseOver, self.imgRect, TextBox.COLOR)
        if self.text:
            static_text_image, r = TextBox.FONT.render(self.text, TextBox.COLOR)
            self.imageBase.blit(static_text_image, self.textTopLeft)
            self.imageMouseOver.blit(static_text_image, self.textTopLeft)

    def __typingImages__(self):
        self.imageMousePress.fill((0, 0, 0))
        gfx.rectangle(self.imageMousePress, self.imgRect, TextBox.COLORP)
        if self.text:
            text_image, r = TextBox.FONT.render(self.text, TextBox.COLORP)
            self.textTopLeft = ((self.rect.width - text_image.get_width()) // 2, (self.rect.height - 
                                                                                  text_image.get_height()) // 2)
            self.imageMousePress.blit(text_image, self.textTopLeft)
        self.image = self.imageMousePress

    def contains_pt(self, pt):
        return self.rect.collidepoint(pt)

    def mouse_over(self):
        if not self.active: 
            self.image = self.imageMouseOver

    def un_mouse_over(self):
        if not self.active: 
            self.image = self.imageBase

    def activate(self):
        self.__typingImages__()
        self.image = self.imageMousePress
        self.active = True

    def add_text(self, c):
        self.text += c
        self.__typingImages__()

    def remove_text(self):
        if len(self.text) > 0:
            self.text = self.text[:-1]
            self.__typingImages__()

    def clear_text(self):
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

    def __init__(self, text, x, y, anchor=None, font=None, text_color=None):
        super().__init__()
        self.text = text
        self.x, self.y = x, y
        self.anchor = anchor
        if font is None: 
            self.font = StatusBox.FONT
        else: 
            self.font = font
        if text_color is None:
            self.textColor = StatusBox.COLOR
        else: 
            self.textColor = text_color
        self.__createImage__()

    def __createImage__(self):
        self.image, r = self.font.render(self.text, self.textColor)
        if self.anchor == 'N':
            top_left = self.x - self.image.get_width() // 2, self.y
        elif self.anchor == 'W':
            top_left = self.x, self.y - self.image.get_height() // 2
        elif self.anchor == 'NW':
            top_left = self.x, self.y
        else:  # default to center
            top_left = (self.x - self.image.get_width() // 2, self.y - self.image.get_height() // 2)
        self.rect = pg.Rect(*top_left, self.image.get_width(), self.image.get_height())

    def update_text(self, text=None, color=None):
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

    def __init__(self, text, x, y, max_w):
        super().__init__()
        self.text = text
        self.x, self.y = x, y
        self.maxW = max_w
        self.__createImage__()

    def __createImage__(self):
        para_list = []
        self.h = 0
        for paragraph in self.text.splitlines():
            sf, h = self.__createParagraphImage__(paragraph)
            para_list.append((sf, h))
            self.h += h + MultilineLabel.PARA_MARGIN
        self.image = pg.Surface((self.maxW, self.h))
        curr_y = 0
        for sf, h in para_list:
            self.image.blit(sf, (0, curr_y))
            curr_y += h + MultilineLabel.PARA_MARGIN

    def __createParagraphImage__(self, text):
        word_list = text.split()
        line_list = []
        line_sf_list = []
        h = 0
        next_line = word_list.pop(0)
        while next_line:
            curr_line, next_line = next_line, ""
            while MultilineLabel.FONT.get_rect(curr_line).width < self.maxW:
                if not word_list:
                    break
                curr_line += " " + word_list.pop(0)
            else:
                curr_line, next_line = curr_line.rsplit(" ", 1)
            line_list.append(curr_line)
        for l in line_list:
            sf, r = MultilineLabel.FONT.render(l, MultilineLabel.COLOR)
            line_sf_list.append((sf, r))
            h += r.height + MultilineLabel.LINE_MARGIN
        image = pg.Surface((self.maxW, h))
        curr_y = 0
        for sf, r in line_sf_list:
            image.blit(sf, (0, curr_y))
            curr_y += r.height + MultilineLabel.LINE_MARGIN
        return image, h

    @property
    def rect(self):
        return pg.Rect(self.x, self.y, self.maxW, self.h)


class SettingsMenu(Menu):
    COLORRED = (255, 0, 0)
    COLORGREEN = (0, 255, 0)
    COLORBLUE = (0, 0, 255)
    COLORYELLOW = (255, 255, 0)
    COLORORANGE = (255, 165, 0)
    COLORPURPLE = (128, 0, 128)

    def __init__(self, w, h, user, main_menu):
        super().__init__(w, h)
        self.star_bg()
        self.mainMenu = main_menu
        self.user = user
        but_w = 300
        self.add_label("Change Name:", w // 2, 230)
        self.add_text_box("Name", pg.Rect((w - but_w) // 2, 250, but_w, 70), default_text=user.name)

        self.add_label("Change Color:", w // 2, 350)
        self.add_color_button("", pg.Rect((w - but_w) // 2, 370, 40, 40), self.COLORRED)
        self.add_color_button("", pg.Rect((w - but_w) // 2 + 52, 370, 40, 40), self.COLORGREEN)
        self.add_color_button("", pg.Rect((w - but_w) // 2 + 104, 370, 40, 40), self.COLORBLUE)
        self.add_color_button("", pg.Rect((w - but_w) // 2 + 156, 370, 40, 40), self.COLORYELLOW)
        self.add_color_button("", pg.Rect((w - but_w) // 2 + 208, 370, 40, 40), self.COLORORANGE)
        self.add_color_button("", pg.Rect((w - but_w) // 2 + 260, 370, 40, 40), self.COLORPURPLE)

        self.add_status_box("status", "", w // 2, 460)
        self.add_button("SAVE", pg.Rect((w - but_w) // 2, 480, but_w, 50), self.validate)
        self.add_button("BACK", pg.Rect((w - but_w) // 2, 540, but_w, 50), main_menu)

    def validate(self):
        # Check values
        new_name = self.get_text_box("Name")
        new_color = self.get_color_button().color_p

        if re.match(r'[a-zA-Z]+[a-zA-Z0-9]*$', new_name) and 3 < len(new_name) < 17:
            self.user.name = new_name
            self.user.color = new_color
            self.mainMenu()
        elif len(new_name) < 4:
            self.get_status_box('status').update_text("Username must be at least 4 characters", self.ERRORCOLOR)
        elif len(new_name) > 16:
            self.get_status_box('status').update_text("Username can't be loner than 16 characters", self.ERRORCOLOR)
        elif new_name == '':
            self.get_status_box('status').update_text("Username can't be blank", self.ERRORCOLOR)
        elif new_name[0].isdigit():
            self.get_status_box('status').update_text("Username can't start with a digit", self.ERRORCOLOR)
        else:
            self.get_status_box('status').update_text("Username contains forbidden symbols", self.ERRORCOLOR)


class StartMPMenu(Menu):

    def __init__(self, w, h, pre_game_menu, main_menu):
        super().__init__(w, h)
        self.star_bg()
        self.preGameMenu = pre_game_menu
        but_w = 300
        self.add_label("Enter room name:", w // 2, 230)
        self.add_text_box("room", pg.Rect((w - but_w) // 2, 250, but_w, 70))
        self.add_label("Number of players (%d-%d):" % (MIN_PLAYERS, MAX_PLAYERS), w // 2, 350)
        self.add_text_box("players", pg.Rect((w - but_w) // 2, 370, but_w, 70))
        self.add_status_box("status", "", w // 2, 480)
        self.add_button("START", pg.Rect((w - but_w) // 2, 500, but_w, 50), self.validate)
        self.add_button("BACK", pg.Rect((w - but_w) // 2, 560, but_w, 50), main_menu)
        self.numPlayers = 2

    def validate(self):
        #Check values
        self.preGameMenu()


class JoinMPMenu(Menu):

    def __init__(self, w, h, main_menu):
        super().__init__(w, h)
        self.star_bg()
        but_w = 300
        self.add_label("Enter the name of room to connect to:", w // 2, 225)
        self.add_text_box("room", pg.Rect((w - but_w) // 2, 250, but_w, 100), self.connect_to_server)
        self.add_status_box("status", "", w // 2, 400)
        self.add_button("CONNECT AND START", pg.Rect((w - but_w) // 2, 440, but_w, 50), self.connect_to_server)
        self.add_button("BACK", pg.Rect((w - but_w) // 2, 500, but_w, 50), main_menu)

    def connect_to_server(self):
        self.update_status_box("status", "Trying to connect...")


class PreGameMenu(Menu):

    def __init__(self, w, h):
        super().__init__(w, h)
        self.add_status_box("status", "", w // 2, 400)
        self.start()

    def start(self):
        self.update_status_box("status", "Waiting for other players...")
