import random
import glob
import math
import pygame

#  -sfx
#  -light coming through window? (remove cross hatch?)

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
C_NONE   = (0, 0, 0, 0)

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
screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.display.set_caption('Laundry Day')


class Sock:

    def __init__(self, img, coords):
        self.pair = None
        self.img = img
        self.x = coords[0]
        self.y = coords[1]
        self.w = img.get_width()
        self.h = img.get_width()

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

light_beam_img = pygame.image.load('art/light_beams.png').convert_alpha()
floor_img = pygame.image.load('art/floor_60.png').convert_alpha()
bed_img = pygame.image.load('art/bed.png').convert_alpha()

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

mainClock = pygame.time.Clock()

# initiate socks {{{
sock_color = [[0, 0, 1, 1, 1],
              [0, 0, 1, 1, 1],
              [0, 0, 1, 1, 1],
              [0, 0, 1, 1, 1],
              [0, 1, 1, 1, 1],
              [1, 1, 1, 1, 1],
              [1, 1, 1, 1, 0],
              [1, 1, 1, 0, 0]]

def init_socks():
    socks = []

    for sock_file in glob.glob("art/socks/*.png"):

        sock_img = pygame.image.load(sock_file).convert_alpha()
        if sock_img.get_width() != SOCK_WIDTH or sock_img.get_height() != SOCK_HEIGHT:
            continue

        valid_sock = True
        for ay, arr in enumerate(sock_color):
            for ax, _ in enumerate(arr):
                if ((not sock_color[ay][ax] and sock_img.get_at((ax, ay))[3] != 0) or
                        (sock_color[ay][ax] and sock_img.get_at((ax, ay))[3] == 0)):
                    valid_sock = False
                    break

            if not valid_sock:
                break

        if not valid_sock:
            continue

        sockA = Sock(sock_img, (random.randrange(0, SCREEN_WIDTH-SOCK_WIDTH),
                     random.randrange(bed_img.get_height()+1, SCREEN_HEIGHT-SOCK_HEIGHT)))
        sockB = Sock(sock_img, (random.randrange(0, SCREEN_WIDTH-SOCK_WIDTH),
                     random.randrange(bed_img.get_height()+1, SCREEN_HEIGHT-SOCK_HEIGHT)))
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

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    ret_val = OPT_QUIT

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == MOUSE_LEFT:
                    # get sock furthest back in the array who is under the mouse
                    held_sock = get_top_item(socks)

                    if held_sock:
                        # put that sock at the back of the list of socks
                        socks.remove(held_sock)
                        socks.append(held_sock)
                        # print(f'picked up {held_sock.color} sock')

            elif event.type == pygame.MOUSEMOTION:
                buttons = pygame.mouse.get_pressed()

                if not held_sock:
                    pygame.mouse.get_rel()
                    # get_rel calculates based off of the last time it was called,
                    #   needs to be called right before picked up
                elif held_sock and buttons[0]:
                    md = pygame.mouse.get_rel()
                    # print(f'mouse delta: {md}')
                    held_sock.x += md[0]/SCALE
                    held_sock.y += md[1]/SCALE

            elif event.type == pygame.MOUSEBUTTONUP:
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

main_menu_bg = pygame.image.load("art/main_menu.png")
# main_menu_bg = pygame.transform.scale(main_menu_bg, (DISPLAY_WIDTH, DISPLAY_HEIGHT))

def main_menu_loop():

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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    ret_val = OPT_QUIT

            elif event.type == pygame.QUIT:
                ret_val = OPT_QUIT

            elif event.type == pygame.MOUSEMOTION:
                mx, my = pygame.mouse.get_pos()
                mx /= SCALE
                my /= SCALE

                for i in range(len(MAIN_MENU_OPTIONS)):
                    if (button_coords[i][0] <= mx <
                            button_coords[i][0] + main_menu_buttons[i*2].get_width() and
                            button_coords[i][1] <= my <
                            button_coords[i][1] + main_menu_buttons[i*2].get_height()):
                        button_hovered = i + 1

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_hovered > OPT_NONE:
                    ret_val = button_hovered

        screen.fill(C_RED)
        screen.blit(main_menu_bg, (0, 0))

        for i in range(len(MAIN_MENU_OPTIONS)):
            screen.blit(main_menu_buttons[i*2], button_coords[i])

        if button_hovered:
            screen.blit(main_menu_buttons[(button_hovered-1)*2 + 1],
                        button_coords[button_hovered-1])

        pygame.transform.scale(screen, (DISPLAY_WIDTH, DISPLAY_HEIGHT), display)

        pygame.display.update()
        mainClock.tick(30)

    return ret_val
# }}}

# how to loop {{{

how_to_imgs = [[pygame.image.load(f'art/how_to_pg0_{i}.png') for i in range(5)],
               [pygame.image.load(f'art/how_to_pg1_{i}.png') for i in range(5)]]

def how_to_loop():

    page_num = 0
    page_imgs = how_to_imgs[page_num]
    start_time = pygame.time.get_ticks()

    ret_val = OPT_NONE
    while not ret_val:

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if page_num == 0:
                    page_num = 1
                    page_imgs = how_to_imgs[page_num]
                    start_time = pygame.time.get_ticks()
                else:
                    if event.key == pygame.K_BACKSPACE:
                        page_num = 0
                        page_imgs = how_to_imgs[page_num]
                        start_time = pygame.time.get_ticks()
                    else:
                        ret_val = OPT_MENU

        screen.fill(C_BLUE)

        time_elapsed = math.floor((pygame.time.get_ticks() - start_time)/500)

        if time_elapsed >= len(page_imgs):
            start_time = pygame.time.get_ticks()
            time_elapsed = 0

        screen.blit(page_imgs[time_elapsed], (0, 0))

        pygame.transform.scale(screen, (DISPLAY_WIDTH, DISPLAY_HEIGHT), display)

        pygame.display.update()
        mainClock.tick(30)

    return ret_val
# }}}

# end screen loop {{{

fade_imgs = [pygame.image.load(f'art/fade{i}.png') for i in range(3)]

end_screen_img = pygame.image.load('art/end_screen.png')

def end_screen():
    done_fading = False
    start_time = pygame.time.get_ticks()

    pygame.time.delay(1000)

    ret_val = OPT_NONE
    while not ret_val:

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                ret_val = OPT_MENU

        screen.fill(C_BLUE)

        time_elapsed = math.floor((pygame.time.get_ticks() - start_time)/1000)

        if done_fading:
            screen.blit(end_screen_img, (0, 0))
        else:
            if time_elapsed >= len(fade_imgs):
                done_fading = True
                screen.blit(end_screen_img, (0, 0))
            else:
                screen.blit(fade_imgs[time_elapsed], (0, 0))

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
    elif menu_choice == OPT_QUIT:
        run_program = False
    elif menu_choice == OPT_SETTINGS:
        how_to_loop()
# }}}

pygame.quit()
