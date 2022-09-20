import random
import glob
import pygame

#  -game end screen
#  -sfx
#  -light coming through window?
#  -error catch an error with the sock folder
#    +numbers not in order, one that isn't a number
#  -custom sock folder? more relaxed with file names? check width of files?

pygame.init()

# Constants {{{
SCREEN_WIDTH = 60
SCREEN_HEIGHT = 60

SCALE = 10

DISPLAY_WIDTH = SCREEN_WIDTH * SCALE
DISPLAY_HEIGHT = SCREEN_HEIGHT * SCALE

SOCK_WIDTH = 5
SOCK_HEIGHT = 8

C_BLACK  = (255, 255, 255, 1)
C_BROWN  = (136, 58, 42, 1)
C_RED    = (255, 0, 0, 1)
C_GREEN  = (0, 255, 0, 1)
C_BLUE   = (0, 0, 255, 1)
C_YELLOW = (255, 255, 0, 1)

# options for what happens on a menu/going between menus
OPT_NONE = 0
OPT_GAME = 1
OPT_SETTINGS = 2
OPT_QUIT = 3
OPT_WIN_GAME = 4
OPT_MENU = 5

MAIN_MENU_OPTIONS = [OPT_GAME, OPT_SETTINGS, OPT_QUIT]

FONT_SIZE = 8
# FONT_SIZE = 32

MOUSE_LEFT = 1
#}}}

display = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
# screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Laundry Day')

# pygame.mouse.set_visible(False)

class Sock:

    def __init__(self, num, rect):
        self.pair = None
        self.img = pygame.image.load(f'art/sock{num}.png').convert_alpha()
        self.x = rect[0]
        self.y = rect[1]
        self.w = rect[2]
        self.h = rect[3]

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

floor_img = pygame.image.load('art/floor_60.png').convert_alpha()
# floor_img = pygame.transform.scale(floor_img, (DISPLAY_WIDTH, DISPLAY_HEIGHT))

light_beam_img = pygame.image.load('art/light_beams.png').convert_alpha()
# light_beam_img = pygame.transform.scale(light_beam_img, (DISPLAY_WIDTH, DISPLAY_HEIGHT))

bed_img = pygame.image.load('art/bed.png').convert_alpha()
# beg_img = pygame.transform.scale(bed_img, (bed_img.get_width()*SCALE, bed_img.get_height()*SCALE))

"""
gets top item from pile that is under cursor

returns item
"""
def get_top_item(pile):
    mx, my = pygame.mouse.get_pos()

    mx /= SCALE
    my /= SCALE

    for item in reversed(pile):
        if item.x <= mx < item.x + item.w:
            if item.y <= my < item.y + item.h:
                return item


    return None

"""
sees if two items/socks overlap

returns bool
"""
def overlaps(a, b):
    if not (a and b):
        return False

    return a.get_rect().colliderect(b.get_rect())

# text {{{
kongtext32 = pygame.font.SysFont("kongtext", FONT_SIZE)
# }}}

mainClock = pygame.time.Clock()

# initiate socks {{{
def init_socks():
    socks = []

    num_pairs = 0
    for _ in glob.glob("art/sock[0-9]*.png"):
        num_pairs += 1

    num_pairs = 2

    for i in range(1, num_pairs+1):
        sockA = Sock(i, (random.randrange(0, SCREEN_WIDTH-SOCK_WIDTH),
                     random.randrange(bed_img.get_height()+1, SCREEN_HEIGHT-SOCK_HEIGHT),
                     5, 8))
        sockB = Sock(i, (random.randrange(0, SCREEN_WIDTH-SOCK_WIDTH),
                     random.randrange(bed_img.get_height()+1, SCREEN_HEIGHT-SOCK_HEIGHT),
                     5, 8))
        sockA.pair = sockB
        sockB.pair = sockA
        socks.append(sockA)
        socks.append(sockB)

    return socks
# }}}

# game loop {{{
def game_loop():

    socks = init_socks()
    held_sock = None

    ret_val = OPT_NONE
    while not ret_val:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ret_val = OPT_QUIT

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    ret_val = OPT_QUIT

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == MOUSE_LEFT:
                    # get sock furthest back in the array who is under the mouse
                    held_sock = get_top_item(socks)

                    if held_sock:
                        # put that sock at the back of the list of socks
                        socks.remove(held_sock)
                        socks.append(held_sock)
                        # print(f'picked up {held_sock.color} sock')

            if event.type == pygame.MOUSEMOTION:
                buttons = pygame.mouse.get_pressed()

                if not held_sock:
                    pygame.mouse.get_rel()
                    # get_rel calculates based off of the last time it was called,
                    #   needs to be called right before picked up
                if held_sock and buttons[0]:
                    md = pygame.mouse.get_rel()
                    # print(f'mouse delta: {md}')
                    held_sock.x += md[0]/SCALE
                    held_sock.y += md[1]/SCALE

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == MOUSE_LEFT:
                    if held_sock:  # check if putting a sock down on its match
                        if overlaps(held_sock, held_sock.pair):
                            held_pair_index = socks.index(held_sock.pair)
                            held_pair = socks[held_pair_index]

                            no_between = True
                            for i in range(held_pair_index+1, len(socks)-1):
                                # ^ ignore redundantly overlap of held_pair and held_sock
                                if overlaps(held_pair, socks[i]):
                                    no_between = False
                                    break

                            if no_between:
                                socks.remove(held_pair)
                                socks.pop()

                                # if array is empty -> game is over
                                if len(socks) <= 0:
                                    ret_val = OPT_WIN_GAME

                    held_sock = None

        screen.fill(C_BROWN)
        screen.blit(floor_img, (0, 0))

        screen.blit(bed_img, (2, 0))

        for sock in socks:
            screen.blit(sock.img, sock.get_rect())

        screen.blit(light_beam_img, (0, 0))

        pygame.transform.scale(screen, (DISPLAY_WIDTH, DISPLAY_HEIGHT), display)

        pygame.display.update()
        mainClock.tick(30)

    return ret_val
# }}}

# main menu loop {{{

main_menu_bg = pygame.image.load("art/main_menu3.png")
# main_menu_bg = pygame.transform.scale(main_menu_bg, (DISPLAY_WIDTH, DISPLAY_HEIGHT))

def main_menu_loop():

    choice = 0  # which MENU OPTION it will select

    # main_menu_text = kongtext32.render("Laundy Day", False, C_BLACK)
    # menu_options_text = [kongtext32.render("PLAY", False, C_BLACK),
    #                      kongtext32.render("SETTINGS", False, C_BLACK),
    #                      kongtext32.render("QUIT", False, C_BLACK)]
    # menu_options_text_sel = [kongtext32.render("PLAY", False, C_YELLOW),
    #                          kongtext32.render("SETTINGS", False, C_YELLOW),
    #                          kongtext32.render("QUIT", False, C_YELLOW)]

    # choice*2 for button, choice*2 + 1 for selected button
    main_menu_buttons = [pygame.image.load('art/play.png'),
                         pygame.image.load('art/play_selected.png'),
                         pygame.image.load('art/how_to.png'),
                         pygame.image.load('art/how_to_selected.png'),
                         pygame.image.load('art/quit.png'),
                         pygame.image.load('art/quit_selected.png')]
    button_coords = [(19, 31),
                     (16, 39),
                     (19, 47)]

    button_hovered = OPT_NONE

    ret_val = OPT_NONE
    while not ret_val:

        for event in pygame.event.get():
            if event.type == pygame.MOUSEMOTION:
                mx, my = pygame.mouse.get_pos()
                mx /= SCALE
                my /= SCALE

                for i in range(len(MAIN_MENU_OPTIONS)):
                    if (button_coords[i][0] <= mx <
                            button_coords[i][0] + main_menu_buttons[i*2].get_width() and
                            button_coords[i][1] <= my <
                            button_coords[i][1] + main_menu_buttons[i*2].get_height()):
                        button_hovered = i + 1

            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_hovered > OPT_NONE:
                    ret_val = button_hovered

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    ret_val = OPT_QUIT
            #     elif event.key == pygame.K_RETURN:
            #         ret_val = MAIN_MENU_OPTIONS[choice]

            #     elif event.key == pygame.K_UP:
            #         choice -= 1
            #     elif event.key == pygame.K_DOWN:
            #         choice += 1

        # if choice < 0:
            # choice = len(MAIN_MENU_OPTIONS) - 1
        # if choice >= len(MAIN_MENU_OPTIONS):
            # choice = 0

        screen.fill(C_RED)
        screen.blit(main_menu_bg, (0, 0))

        #{{{
        # for i in range(len(MAIN_MENU_OPTIONS)):
        #     screen.blit(menu_options_text[i],
        #                     (SCREEN_WIDTH/2 - menu_options_text[i].get_width()/2,
        #                      SCREEN_HEIGHT/2 + FONT_SIZE*i*1.5))

        # screen.blit(menu_options_text_sel[choice],
        #                 (SCREEN_WIDTH/2 - menu_options_text_sel[choice].get_width()/2,
        #                  SCREEN_HEIGHT/2 + FONT_SIZE*choice*1.5))

        # screen.blit(main_menu_text,
        #                 (DISPLAY_WIDTH/2 - main_menu_text.get_width()/2,
        #                  FONT_SIZE*4))
        # }}}

        for i in range(len(MAIN_MENU_OPTIONS)):
            screen.blit(main_menu_buttons[i*2], button_coords[i])

        # screen.blit(main_menu_buttons[choice*2 + 1], button_coords[choice])

        if button_hovered:
            screen.blit(main_menu_buttons[(button_hovered-1)*2 + 1],
                        button_coords[button_hovered-1])

        pygame.transform.scale(screen, (DISPLAY_WIDTH, DISPLAY_HEIGHT), display)

        pygame.display.update()
        mainClock.tick(30)

    return ret_val
# }}}

# settings loop {{{

def settings_loop():
    settings_menu_text = kongtext32.render("Settings", False, C_BLACK)

    ret_val = OPT_NONE
    while not ret_val:

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                ret_val = OPT_MENU

        screen.fill(C_BLUE)

        screen.blit(settings_menu_text,
                        (SCREEN_WIDTH/2 - settings_menu_text.get_width()/2,
                         FONT_SIZE))

        pygame.transform.scale(screen, (DISPLAY_WIDTH, DISPLAY_HEIGHT), display)

        pygame.display.update()
        mainClock.tick(30)

    return ret_val
# }}}

# end screen loop {{{
def end_screen():
    ret_val = OPT_NONE
    while not ret_val:

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                ret_val = OPT_MENU

        screen.fill(C_BLUE)

        pygame.transform.scale(screen, (DISPLAY_WIDTH, DISPLAY_HEIGHT), display)

        pygame.display.update()
        mainClock.tick(30)
# }}}

# program loop {{{
run_program = True
while run_program:
    menu_choice = main_menu_loop()

    if menu_choice == OPT_GAME:
        if game_loop() == OPT_WIN_GAME:
            end_screen()
            bed_img = pygame.image.load('art/clean_bed.png').convert_alpha()
    elif menu_choice == OPT_QUIT:
        run_program = False
    elif menu_choice == OPT_SETTINGS:
        settings_loop()
# }}}

pygame.quit()
