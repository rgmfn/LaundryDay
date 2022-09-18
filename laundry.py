import pygame
import random

# TODO
#  -make (better) wood floor
#  -sfx
#  -game end screen
#  -main menu
#  -automatic sense number of socks

pygame.init()

# Constants {{{
WINDOW_WIDTH = 600  # window width
WINDOW_HEIGHT = 600  # window height

SCALE = 20

SOCK_WIDTH = 5 * SCALE
SOCK_HEIGHT = 8 * SCALE

C_BLACK = (255, 255, 255, 1)
C_BROWN = (136, 58, 42, 1)
C_RED   = (255, 0, 0, 1)
C_BLUE  = (0, 0, 255, 1)

OPT_NONE = 0
OPT_GAME = 1
OPT_QUIT = 2
OPT_SETTINGS = 3
OPT_WIN_GAME = 4

MOUSE_LEFT = 1
#}}}

display = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Laundry Day!')

class Sock:

    def __init__(self, num, rect):
        self.pair = None
        self.img = pygame.image.load(f'art/sock{num}.png').convert_alpha()
        self.x = rect[0]
        self.y = rect[1]
        self.w = rect[2] * SCALE
        self.h = rect[3] * SCALE
        self.img = pygame.transform.scale(self.img, (self.w, self.h))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

floor_img = pygame.image.load('art/floor1.png').convert_alpha()
floor_img = pygame.transform.scale(floor_img, (WINDOW_WIDTH, WINDOW_HEIGHT))

"""
gets top item from pile that is under cursor

returns item
"""
def get_top_item(pile):
    mx, my = pygame.mouse.get_pos()

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

    # if (not a) or (not b):
    #     return False

    return a.get_rect().colliderect(b.get_rect())

mainClock = pygame.time.Clock()

# initiate socks {{{
def initiate_socks():
    socks = []

    # NUM_PAIRS = 22
    # TODO ^ make automatic
    NUM_PAIRS = 2
    for i in range(1, NUM_PAIRS+1):
        sockA = Sock(i, (random.randrange(0, WINDOW_WIDTH-SOCK_WIDTH),
                     random.randrange(0, WINDOW_HEIGHT-SOCK_HEIGHT),
                     5, 8))
        sockB = Sock(i, (random.randrange(0, WINDOW_WIDTH-SOCK_WIDTH),
                     random.randrange(0, WINDOW_HEIGHT-SOCK_HEIGHT),
                     5, 8))
        sockA.pair = sockB
        sockB.pair = sockA
        socks.append(sockA)
        socks.append(sockB)

    return socks
# }}}

# game loop {{{
def game_loop():

    socks = initiate_socks()
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
                    held_sock.x += md[0]
                    held_sock.y += md[1]

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

        display.fill(C_BROWN)
        display.blit(floor_img, (0, 0))

        for sock in socks:
            display.blit(sock.img, sock.get_rect())

        pygame.display.update()
        mainClock.tick(30)

    return ret_val
# }}}

# menu loop {{{
def menu_loop():
    ret_val = OPT_NONE

    while not ret_val:

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    ret_val = OPT_QUIT
                if event.key == pygame.K_RETURN:
                    ret_val = OPT_GAME

        display.fill(C_RED)

        pygame.display.update()
        mainClock.tick(30)

    return ret_val
# }}}

# end screen loop {{{
def end_screen():
    run_end_screen = True
    while run_end_screen:

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                run_end_screen = False

        display.fill(C_BLUE)

        pygame.display.update()
        mainClock.tick(30)
# }}}

# program loop {{{
run_program = True
while run_program:
    menu_choice = menu_loop()

    if menu_choice == OPT_GAME:
        if game_loop() == OPT_WIN_GAME:
            end_screen()
    elif menu_choice == OPT_QUIT:
        run_program = False
# }}}

pygame.quit()
