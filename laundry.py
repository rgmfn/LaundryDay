import pygame

# TODO
#  -make wood floor

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

    def __init__(self, num, color, rect):
        self.pair = None
        self.img = pygame.image.load(f'art/sock{num}.png').convert_alpha()
        self.color = color
        self.x = rect[0]
        self.y = rect[1]
        self.w = rect[2] * 3
        self.h = rect[3] * 3
        self.img = pygame.transform.scale(self.img, (self.w, self.h))

    def get_rect(self):
        return (self.x, self.y, self.w, self.h)

sock1 = Sock(1, (255, 0, 0), (30, 30, 20, 20))
sock3 = Sock(2, (0, 255, 0), (60, 60, 20, 20))

socks = [sock1, sock3]
held_sock = None

"""
gets top item from pile that is under cursor
"""
def get_top_item(pile):
    mx, my = pygame.mouse.get_pos()

    for item in reversed(pile):
        if item.x <= mx < item.x + item.w:
            if item.y <= my < item.y + item.h:
                return item

    return None

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
                held_sock = None

    display.fill(C_BROWN)  # white

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
