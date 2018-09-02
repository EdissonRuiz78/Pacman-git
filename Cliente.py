import zmq
import sys
import pygame
#import threading

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
#pygame.mixer.music.play(-1, 0.0)

context = zmq.Context()

# Clase para representar el juego
class Muro():
    def __init__(self, x, y, width, height, color):
        self.image = pygame.Surface([width, height])
        self.rect = self.image.get_rect()
        self.image.fill(color)
        self.rect.top = y
        self.rect.left = x
        self.x = x
        self.y = y
        self.w = width
        self.h = height
        self.dib = True

class Galleta_p():
    def __init__(self, color, width, height):
        self.image = pygame.Surface([width, height])
        self.rect = self.image.get_rect()
        self.image.fill(white)
        pygame.draw.ellipse(self.image, color, [0, 0, width, height])
        self.dib = True

# Creando los jugadores
class Jugador():
    # Velocidad de cambio
    change_x = 0
    change_y = 0

    def __init__(self, filename):
        self.image = pygame.image.load(filename)
        self.rect = self.image.get_rect()
        self.dib = False # Variable que determine si se dibuja en pantalla

    def camb_dib(self):
        self.dib = not self.dib

    def act_pos(self, pos):
        self.rect.left = pos[0]
        self.rect.top = pos[1]


class Sprites():
    def __init__(self):
        self.lista = []

    def agregar_lista(self, paredes):
        for pared in paredes:
            self.lista.append(pared)

    def agregar(self, elem):
        self.lista.append(elem)

    def dibujar(self, screen):
        for sprite in self.lista:
            if sprite.dib:
                screen.blit(sprite.image, sprite.rect)

#---------------------
# FUNCIONES

# Saber si hay un muro
def hay_muro(pos, muros):
    for muro in muros:
        if (pos[0] >= muro.x and pos[0] <= muro.x + muro.h) and (pos[1] >= muro.y and pos[1] <= muro.y + muro.w):
            return True
    return False

# Creando el mapa
def paredes():
    lista_paredes = []
    # Muros representando la matriz asi: [x, y, width, height]
    muros = [[0, 0, 6, 600],
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
    for muro in muros:
        wall = Muro(muro[0], muro[1], muro[2], muro[3], white)
        lista_paredes.append(wall)
    return lista_paredes

def startGame():
    sprites = Sprites()

    # Crear paredes
    lista_paredes = paredes()
    # Agregar cada sprite de pared a la lista de sprites
    sprites.agregar_lista(lista_paredes)

  # Create the player paddle object
    jugador = Jugador("images/pacman.png")
    sprites.agregar(jugador)

  # Agregar las galletas pequeñas
    lista_galletas = []
    for row in range(19):
        for column in range(19):
            if (row == 7 or row == 8) and (column == 8 or column == 9 or column == 10):
                continue
            else:
                galleta = Galleta_p(yellow, 4, 4)

            # Definir posicion gposiciones_jugalleta pequeña
            galleta.rect.x = (30*column+6)+26
            galleta.rect.y = (30*row+6)+26
            if hay_muro((galleta.rect.x, galleta.rect.y), lista_paredes):
                continue
            else:
                # Agregar galleta a los sprites
                lista_galletas.append(galleta)
                sprites.agregar(galleta)

    bll = len(lista_galletas)
    score = -1
    done = False

    # CONECTARSE CON EL SERVIDOR
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:4444")

    # Manifestar conexión
    socket.send_json({"tipo":"connect", "id":sys.argv[1]})

    # Recibir mensaje, debe ser tipo OK y contener la posicion si fue correcto
    resp = socket.recv_json()
    print("RESPUESTA: ", resp)
    if resp["resp"] == "connect":
        # Establecer posicon del jugador
        jugador.act_pos(resp["pos"])
        # Cambiar estado, se puede dibujar en pantalla al jugador
        jugador.camb_dib()

        # Solicitar inicio de juego
        resp_i = "No" # Mandar constantemente mensajes
        cant_i = 0 # Conectados al momento
        print("Esperando los otros jugadores para iniciar partida...")
        while resp_i == "No":
            socket.send_json({"tipo":"init"})
            resp = socket.recv_json()
            resp_i = resp["resp"]
            cant_a = cant_i # cant_a -> Cantidad recibida actualmente
            cant_i = resp["cant"] # Recibir cantidad nueva

            if resp_i == "No" and not(cant_i == cant_a):
                print("Se conecto un nuevo jugador ({0})".format(cant_i))
            elif resp_i == "Si":
                print("SE CONECTARON TODOS LOS JUGADORES...")
                print("Iniciando...")

        # Iniciar graficos
        pygame.init()
        screen = pygame.display.set_mode([606, 606])
        pygame.display.set_caption('Pacman')
        background = pygame.Surface(screen.get_size())
        background.fill(black)
        clock = pygame.time.Clock()
        pygame.font.init()
        font = pygame.font.Font("freesansbold.ttf", 24)

    else:
        print("OCURRIO UN ERROR AL CONECTARSE")
        exit()


    while done == False:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    print("IZQ")
                    #Pacman.changespeed(-30, 0)
                if event.key == pygame.K_RIGHT:
                    print("DER")
                    #Pacman.changespeed(30, 0)
                if event.key == pygame.K_UP:
                    print("ARR")
                    #Pacman.changespeed(0, -30)
                if event.key == pygame.K_DOWN:
                    print("ABA")
                    #Pacman.changespeed(0, 30)

            #if event.type == pygame.KEYUP:
            #    if event.key == pygame.K_LEFT:
                    #Pacman.changespeed(30, 0)
            #    if event.key == pygame.K_RIGHT:
                    #Pacman.changespeed(-30, 0)
            #    if event.key == pygame.K_UP:
                    #Pacman.changespeed(0, 30)
            #    if event.key == pygame.K_DOWN:
                    #Pacman.changespeed(0, -30)

        # ALL EVENT PROCESSING SHOULD GO ABOVE THIS COMMENT

        # ALL GAME LOGIC SHOULD GO BELOW THIS COMMENT
        #Pacman.update(lista_paredes)#, gate)
        # p_turn = returned[0]
        # p_steps = returned[1]

        # See if the Pacman block has collided with anything.
        #blocks_hit_list = pygame.sprite.spritecollide(Pacman, block_list, True)

        # Check the list of collisions.
        #if len(blocks_hit_list) > 0:
        #    score += len(blocks_hit_list)

            # ALL GAME LOGIC SHOULD GO ABOVE THIS COMMENT

            # ALL CODE TO DRAW SHOULD GO BELOW THIS COMMENT
        screen.fill(black)
        sprites.dibujar(screen)
        #gate.draw(screen)
        #all_sprites_list.draw(screen)
        #monsta_list.draw(screen)
        text = font.render("Score: "+str(score)+"/"+str(bll), True, red)
        screen.blit(text, [10, 10])

        if score == bll:
            print("Gano")
            break

        pygame.display.flip()

        clock.tick(10)


startGame()
pygame.quit()
