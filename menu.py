import  pygame, sys, copy
from pygame.locals import *
from input_box import InputBox

class Menu():
    def __init__(self, screen, user):
        # List of main menu items
        self.items = [(300, 200, 'Settings', (250, 250, 30), (250, 30, 250), 0),
                 (300, 240, 'Quit', (250, 250, 30), (250, 30, 250), 1)]

        # List of settings menu items
        self.settings_items = [(300, 280, 'Save', (250, 250, 30), (250, 30, 250), 0),
                 (300, 320, 'Back', (250, 250, 30), (250, 30, 250), 1)]

        self.screen = screen
        self.user = user
        self.font = pygame.font.SysFont("None", 50)
        self.error_font = pygame.font.SysFont("None", 25)

    def render(self, surface, num_item, items):
        for i in items:
            if num_item == i[5]:
                surface.blit(self.font.render(i[2], 1, i[4]), (i[0], i[1]))
            else:
                surface.blit(self.font.render(i[2], 1, i[3]), (i[0], i[1]))

    def open_menu(self):
        surface = pygame.Surface((800, 600))
        menuLoop = True
        item = 0

        while menuLoop:
            # Getting mouse position
            mp = pygame.mouse.get_pos()

            # Selecting main menu item
            for i in self.items:
                if mp[0]>i[0] and mp[0]<i[0]+155 and mp[1]>i[1] and mp[1]<i[1]+50:
                    item = i[5]

            # Drawing main menu items
            self.render(surface, item, self.items)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # checking what item is selected
                    if item == 0:
                        self.open_settings()
                    elif item == 1:
                        sys.exit()

            # Displaying menu surface on screen
            self.screen.blit(surface, (0, 0))
            pygame.display.flip()

    def open_settings(self):
        surface = pygame.Surface((800, 600))

        # Creating input box for username
        input_box = InputBox(300, 200, 140, 32, self.user.name)

        # Copying user settings in temporary variable
        temp_user = copy.deepcopy(self.user)

        # Creating list of colors and list of color rectangles to check collisions
        color_list = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        color_colliders = [{'rect': pygame.Rect((400, 240, 40, 40)), 'color': temp_user.color}]

        color_choosed = True
        settingsLoop = True
        item = 0
        error_message = ''

        while settingsLoop:
            surface.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                    # Checking what settings item was selected
                    if item == 0:
                        if input_box.text == '':
                            error_message = "Username can't be blank"
                        else:
                            # Copying temporary user to user
                            temp_user.name = input_box.text
                            self.user = copy.deepcopy(temp_user)

                            # Quitting settings
                            settingsLoop = False
                    elif item == 1:
                        settingsLoop = False

                    for item in color_colliders:

                        # Checking collisisons of mouse button with color rectangles
                        if item['rect'].collidepoint(event.pos):

                            # Checking if color list is dropped down
                            if color_choosed:
                                color_choosed = False

                                # Removing current user color from color list to display only other colors
                                color_list.remove(temp_user.color)

                                for color in color_list:

                                    # Creating collision rectangles for other colors
                                    color_colliders.append({'rect': pygame.Rect((400, 240 + len(color_colliders) * 50, 40, 40)),
                                                            'color': color})
                            else:
                                color_choosed = True

                                # Returning current user color back to color list
                                color_list.append(temp_user.color)

                                # Changing temporary user color to choosen one
                                temp_user.color = item['color']

                                # Reassignment collision rectangle's list, keeping rectangle of current user color
                                color_colliders = [{'rect': pygame.Rect((400, 240, 40, 40)), 'color': temp_user.color}]
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        settingsLoop = False
                input_box.handle_event(event)

            input_box.update()
            input_box.draw(surface)

            surface.blit(self.error_font.render(error_message, 1, (255, 0, 0)), (510, 220))
            surface.blit(self.font.render('Color', 1, (255, 255, 255)), (300, 240))

            # Drawing color circle for each collider
            for item in color_colliders:
                pygame.draw.circle(surface, item['color'], (420, item['rect'].y + 20), 20)

            # Getting mouse position
            mp = pygame.mouse.get_pos()

            # Selecting settings item
            for i in self.settings_items:
                if mp[0]>i[0] and mp[0]<i[0]+80 and mp[1]>i[1] and mp[1]<i[1]+50:
                    item = i[5]

            # Drawing settings items
            self.render(surface, item, self.settings_items)

            # Displaying settings surface on screen
            self.screen.blit(surface, (0, 0))
            pygame.display.flip()
