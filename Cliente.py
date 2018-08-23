import zmq
import sys
import pygame
import threading

black = (0, 0, 0)
white = (255, 255, 255)
blue = (0, 0, 255)
green = (0, 255, 0)
red = (255, 0, 0)
purple = (255, 0, 255)
yellow = (255, 255, 0)

pacman = pygame.image.load('images/pacman.png')
pygame.display.set_icon(pacman)
pygame.mixer.init()
pygame.mixer.music.load('pacman.mp3')
pygame.mixer.music.play(-1, 0.0)

# Clase para representar el juego
class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.top = y
        self.rect.left = x

# Creando el mapa
def Room(all_sprites_list):
    wall_list = pygame.sprite.RenderPlain()
    # Muros representando la matriz asi: [x, y, width, height]
    walls = [[0, 0, 6, 600],
             [0, 0, 600, 6],
             [0, 600, 606, 6],
             [600, 0, 6, 606],
             [300, 0, 6, 66],
             [60, 60, 186, 6],
             [360, 60, 186, 6],
             [60, 120, 66, 6],
             [60, 120, 6, 126],
             [180, 120, 246, 6],
             [300, 120, 6, 66],
             [480, 120, 66, 6],
             [540, 120, 6, 126],
             [120, 180, 126, 6],
             [120, 180, 6, 126],
             [360, 180, 126, 6],
             [480, 180, 6, 126],
             [180, 240, 6, 126],
             [180, 360, 246, 6],
             [420, 240, 6, 126],
             [240, 240, 42, 6],
             [324, 240, 42, 6],
             [240, 240, 6, 66],
             [240, 300, 126, 6],
             [360, 240, 6, 66],
             [0, 300, 66, 6],
             [540, 300, 66, 6],
             [60, 360, 66, 6],
             [60, 360, 6, 186],
             [480, 360, 66, 6],
             [540, 360, 6, 186],
             [120, 420, 366, 6],
             [120, 420, 6, 66],
             [480, 420, 6, 66],
             [180, 480, 246, 6],
             [300, 480, 6, 66],
             [120, 540, 126, 6],
             [360, 540, 126, 6]
             ]
    # Loop creando los muros de la lista
    for item in walls:
        wall = Wall(item[0], item[1], item[2], item[3], white)
        wall_list.add(wall)
        all_sprites_list.add(wall)
    return wall_list

# Puerta principal donde salen los fantasmas
def Gate(all_sprites_list):
    gate = pygame.sprite.RenderPlain()
    gate.add(Wall(282, 242, 42, 2, black))
    all_sprites_list.add(gate)
    return gate

class Block(pygame.sprite.Sprite):
    def __init__(self, color, width, height):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([width, height])
        self.image.fill(white)
        self.image.set_colorkey(white)
        pygame.draw.ellipse(self.image, color, [0, 0, width, height])
        self.rect = self.image.get_rect()

# Creando los jugadores
class Player(pygame.sprite.Sprite):
    # Velocidad de cambio
    change_x = 0
    change_y = 0

    def __init__(self, x, y, filename):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(filename).convert()
        self.rect = self.image.get_rect()
        self.rect.top = y
        self.rect.left = x
        self.prev_x = x
        self.prev_y = y

    # Actualizando la velocidad del Jugador
    def prevdirection(self):
        self.prev_x = self.change_x
        self.prev_y = self.change_y

    # Cambio de velocidad del Jugador
    def changespeed(self, x, y):
        self.change_x += x
        self.change_y += y

    # Actualizar posicion del Jugador
    def update(self, walls, gate):
        old_x = self.rect.left
        new_x = old_x+self.change_x
        prev_x = old_x+self.prev_x
        self.rect.left = new_x
        old_y = self.rect.top
        new_y = old_y+self.change_y
        prev_y = old_y+self.prev_y

        # Colisiones contra los Muros
        x_collide = pygame.sprite.spritecollide(self, walls, False)
        if x_collide:
            self.rect.left = old_x
        else:
            self.rect.top = new_y
            y_collide = pygame.sprite.spritecollide(self, walls, False)
            if y_collide:
                self.rect.top = old_y

        if gate != False:
            gate_hit = pygame.sprite.spritecollide(self, gate, False)
            if gate_hit:
                self.rect.left = old_x
                self.rect.top = old_y

class Ghost(Player):
    def changespeed(self, list, ghost, turn, steps, l):
        try:
            z = list[turn][2]
            if steps < z:
                self.change_x = list[turn][0]
                self.change_y = list[turn][1]
                steps += 1
            else:
                if turn < l:
                    turn += 1
                elif ghost == "clyde":
                    turn = 2
                else:
                    turn = 0
                self.change_x = list[turn][0]
                self.change_y = list[turn][1]
                steps = 0
            return [turn, steps]
        except IndexError:
            return [0, 0]

# Call this function so the Pygame library can initialize itself
pygame.init()
# Create an 606x606 sized screen
screen = pygame.display.set_mode([606, 606])
# This is a list of 'sprites.' Each block in the program is
# added to this list. The list is managed by a class called 'RenderPlain.'
# Set the title of the window
pygame.display.set_caption('Pacman')
# Create a surface we can draw on
background = pygame.Surface(screen.get_size())
# Used for converting color maps and such
background = background.convert()
# Fill the screen with a black background
background.fill(black)
clock = pygame.time.Clock()
pygame.font.init()
font = pygame.font.Font("freesansbold.ttf", 24)

# default locations for Pacman and monstas
w = 303-16  # Width
p_h = (7*60)+19  # Pacman height

def startGame():
    # Begin network
    context = zmq.Context()
    socket = context.socket(zmq.DEALER)
    identity = sys.argv[1].encode('ascii')
    socket.identity = identity
    socket.connect("tcp://192.168.60.101:4444")
    print("Started client with id {}".format(identity))
    poller = zmq.Poller()
    poller.register(sys.stdin, zmq.POLLIN)
    poller.register(socket, zmq.POLLIN)
    command = "Move$connect"
    dest, msg = command.split('$', 1)
    print (dest, msg)
    socket.send_multipart([bytes(dest, 'ascii'), bytes(msg, 'ascii')])
    # End network

    # Begin Graphics
    all_sprites_list = pygame.sprite.RenderPlain()
    block_list = pygame.sprite.RenderPlain()
    monsta_list = pygame.sprite.RenderPlain()
    pacman_collide = pygame.sprite.RenderPlain()
    wall_list = Room(all_sprites_list)
    gate = Gate(all_sprites_list)

    p_turn = 0
    p_steps = 0

  # Create the player paddle object
    Pacman = Player(w, p_h, "images/pacman.png")
    all_sprites_list.add(Pacman)
    pacman_collide.add(Pacman)

  # Draw the grid
    for row in range(19):
        for column in range(19):
            if (row == 7 or row == 8) and (column == 8 or column == 9 or column == 10):
                continue
            else:
                block = Block(yellow, 4, 4)

            # Set a random location for the block
            block.rect.x = (30*column+6)+26
            block.rect.y = (30*row+6)+26
            b_collide = pygame.sprite.spritecollide(block, wall_list, False)
            p_collide = pygame.sprite.spritecollide(
                block, pacman_collide, False)
            if b_collide:
                continue
            elif p_collide:
                continue
            else:
                # Add the block to the list of objects
                block_list.add(block)
                all_sprites_list.add(block)

    bll = len(block_list)
    score = 0
    done = False
    i = 0

    while done == False:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    Pacman.changespeed(-30, 0)
                    command = "Move$Izquierda"
                    dest, msg = command.split('$', 1)
                    print (dest, msg)
                    socket.send_multipart([bytes(dest, 'ascii'), bytes(msg, 'ascii')])
                if event.key == pygame.K_RIGHT:
                    Pacman.changespeed(30, 0)
                    command = "Move$Derecha"
                    dest, msg = command.split('$', 1)
                    print (dest, msg)
                    socket.send_multipart([bytes(dest, 'ascii'), bytes(msg, 'ascii')])
                if event.key == pygame.K_UP:
                    Pacman.changespeed(0, -30)
                    command = "Move$Arriba"
                    dest, msg = command.split('$', 1)
                    print (dest, msg)
                    socket.send_multipart([bytes(dest, 'ascii'), bytes(msg, 'ascii')])
                if event.key == pygame.K_DOWN:
                    command = "Move$Abajo"
                    dest, msg = command.split('$', 1)
                    print (dest, msg)
                    socket.send_multipart([bytes(dest, 'ascii'), bytes(msg, 'ascii')])
                    Pacman.changespeed(0, 30)

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    Pacman.changespeed(30, 0)
                if event.key == pygame.K_RIGHT:
                    Pacman.changespeed(-30, 0)
                if event.key == pygame.K_UP:
                    Pacman.changespeed(0, 30)
                if event.key == pygame.K_DOWN:
                    Pacman.changespeed(0, -30)

        # ALL EVENT PROCESSING SHOULD GO ABOVE THIS COMMENT

        # ALL GAME LOGIC SHOULD GO BELOW THIS COMMENT
        Pacman.update(wall_list, gate)
        # p_turn = returned[0]
        # p_steps = returned[1]

        # See if the Pacman block has collided with anything.
        blocks_hit_list = pygame.sprite.spritecollide(Pacman, block_list, True)

        # Check the list of collisions.
        if len(blocks_hit_list) > 0:
            score += len(blocks_hit_list)

            # ALL GAME LOGIC SHOULD GO ABOVE THIS COMMENT

            # ALL CODE TO DRAW SHOULD GO BELOW THIS COMMENT
        screen.fill(black)
        wall_list.draw(screen)
        gate.draw(screen)
        all_sprites_list.draw(screen)
        monsta_list.draw(screen)
        text = font.render("Score: "+str(score)+"/"+str(bll), True, red)
        screen.blit(text, [10, 10])

        if score == bll:
            doNext("Congratulations, you won!", 145, all_sprites_list,
                block_list, monsta_list, pacman_collide, wall_list, gate)
            monsta_hit_list = pygame.sprite.spritecollide(
                Pacman, monsta_list, False)

        if monsta_list:
            doNext("Game Over", 235, all_sprites_list, block_list,
                monsta_list, pacman_collide, wall_list, gate)

            # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT

        pygame.display.flip()

        clock.tick(10)


def doNext(message, left, all_sprites_list, block_list, monsta_list, pacman_collide, wall_list, gate):
    while True:
        # ALL EVENT PROCESSING SHOULD GO BELOW THIS COMMENT
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                if event.key == pygame.K_RETURN:
                    del all_sprites_list
                    del block_list
                    del monsta_list
                    del pacman_collide
                    del wall_list
                    del gate
                    startGame()

        # Grey background
        w = pygame.Surface((400, 200))  # the size of your rect
        w.set_alpha(10)                # alpha level
        w.fill((128, 128, 128))           # this fills the entire surface
        screen.blit(w, (100, 200))    # (0,0) are the top-left coordinates

        #Won or lost
        text1 = font.render(message, True, white)
        screen.blit(text1, [left, 233])

        text2 = font.render("To play again, press ENTER.", True, white)
        screen.blit(text2, [135, 303])
        text3 = font.render("To quit, press ESCAPE.", True, white)
        screen.blit(text3, [165, 333])

        pygame.display.flip()
        clock.tick(10)

def server_interaction(Pacman):
    interaction = not True
    while interaction:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                interaction = False

startGame()
pygame.quit()
