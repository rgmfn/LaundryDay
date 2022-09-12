import pygame

# TODO
#  -make (better) wood floor

pygame.init()

# Constants {{{
WW = 600  # window width
WH = 600  # window height

SW = 30

C_BROWN = (136, 58, 42, 1)

MOUSE_LEFT = 1
#}}}

display = pygame.display.set_mode((WW, WH))
pygame.display.set_caption('Laundry Day!')

class Sock:

    def __init__(self, num, rect):
        self.pair = None
        self.img = pygame.image.load(f'art/sock{num}.png').convert_alpha()
        self.x = rect[0]
        self.y = rect[1]
        self.w = rect[2] * 10
        self.h = rect[3] * 10
        self.img = pygame.transform.scale(self.img, (self.w, self.h))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

sock1 = Sock(3, (30, 30, 5, 8))
sock2 = Sock(3, (30, 120, 5, 8))
sock1.pair = sock2
sock2.pair = sock1
sock3 = Sock(4, (60, 60, 5, 8))
sock4 = Sock(4, (60, 120, 5, 8))
sock3.pair = sock4
sock4.pair = sock3

socks = [sock1, sock2, sock3, sock4]
held_sock = None

floor_img = pygame.image.load('art/floor1.png').convert_alpha()
floor_img = pygame.transform.scale(floor_img, (600, 600))

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

    if (not a) or (not b):
        return False

    return a.get_rect().colliderect(b.get_rect())

mainClock = pygame.time.Clock()

run = True
while run:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False

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
                # check if match:
                # 1. make sure held sock and its pair overlap
                if overlaps(held_sock, held_sock.pair):
                    # 2. find other pair in socks arr
                    held_pair_index = socks.index(held_sock.pair)
                    held_pair = socks[held_pair_index]
                    # 3. make sure no socks between them overlap the pair sock
                    #      (the pair sock is on top)
                    no_between = True
                    for i in range(held_pair_index+1, len(socks)-1):
                        if overlaps(held_pair, socks[i]):
                            no_between = False
                            break

                    if no_between:
                        socks.remove(held_pair)
                        socks.pop()

                held_sock = None

    display.fill(C_BROWN)  # white
    display.blit(floor_img, (0, 0))

    # delta = pygame.mouse.get_rel()
    # print(f'dx: {delta[0]}, dy: {delta[1]}')

    for sock in socks:
        # pygame.draw.rect(display, sock.color, sock.get_rect())
        display.blit(sock.img, sock.get_rect())

    # pygame.draw.rect(display, sock3.color, sock3.pos)

    # display.blit()
    pygame.display.update()
    mainClock.tick(30)

pygame.quit()
