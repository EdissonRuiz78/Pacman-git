import zmq
import sys
import pygame
import random
#import threading

black = (0, 0, 0)
white = (255, 255, 255)
blue = (0, 0, 255)
green = (0, 255, 0)
red = (255, 0, 0)
purple = (255, 0, 255)
yellow = (255, 255, 0)

# Cargar Imagenes
pacman_img = 'images/pacman.png'
pacman_ene_img = "images/pacman-ene.png"
fantasma_img = 'images/fantasma.png'
fantasma_ene_img = "images/fantasma-ene.png"

#pygame.display.set_icon(pacman_img)
pygame.mixer.init()
pygame.mixer.music.load('pacman.mp3')
#pygame.mixer.music.play(-1, 0.0)

context = zmq.Context()

# Clase para representar el juego
class Muro(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color):
        pygame.sprite.Sprite.__init__(self)
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
        self.ide = ""

class Galleta_p(pygame.sprite.Sprite):
    def __init__(self, color, width, height):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([width, height])
        self.rect = self.image.get_rect()
        self.image.fill(white)
        pygame.draw.ellipse(self.image, color, [0, 0, width, height])
        self.dib = True
        self.color = color
        self.esp = False
        self.ide = ""

# Creando los jugadores
class Jugador(pygame.sprite.Sprite):
    def __init__(self, filename, ide):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(filename)
        self.rect = self.image.get_rect()
        self.ide = ide
        self.dib = False # Variable que determine si se dibuja en pantalla
        self.conv = False
        self.eneconv = False
        self.elim = False

    def camb_img(self, filename):
        self.image = pygame.image.load(filename)

    # Metodo para cambiar variable de dibujo
    def camb_dib(self):
        self.dib = not self.dib

    # Metodo para retornar posicion
    def ret_pos(self):
        return (self.rect.left, self.rect.top)

    # Metodo para actualizar posicion
    def act_pos(self, pos):
        self.rect.left = pos[0]
        self.rect.top = pos[1]
        self.x = self.rect.left
        self.y = self.rect.top

class Sprites():
    def __init__(self):
        self.lista = []

    def agregar_lista(self, paredes):
        for pared in paredes:
            self.lista.append(pared)

    def agregar(self, elem):
        self.lista.append(elem)
        return self.lista.index(elem)

    def actualizar(self, elem):
        index = self.lista.index(elem)
        self.lista[index].rect.left = elem.rect.left
        self.lista[index].rect.top = elem.rect.top

    def buscar(self, sprite):
        self.lista[self.lista.index(sprite)].dib = False

    def eliminar(self, ide):
        for elem in self.lista:
            if elem.ide == ide:
                self.lista.remove(elem)

    def dibujar(self, screen):
        for sprite in self.lista:
            if sprite.dib:
                screen.blit(sprite.image, sprite.rect)

#---------------------
# FUNCIONES

# Creando el mapa
def paredes():
    lista_paredes = []
    lista_w = pygame.sprite.RenderPlain()
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
        lista_w.add(wall)
        lista_paredes.append(wall)
    return lista_paredes, lista_w

def startGame():
    sprites = Sprites()

    # Crear paredes
    lista_paredes, lista_w = paredes()
    # Agregar cada sprite de pared a la lista de sprites
    sprites.agregar_lista(lista_paredes)

  # Create the player paddle object
    ide = sys.argv[1]
    jugador = Jugador(pacman_img, ide)
    sprites.agregar(jugador)

    # CONECTARSE CON EL SERVIDOR
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:4444")

    # Manifestar conexión
    socket.send_json({"tipo":"connect", "id":ide})

    # Recibir mensaje, debe ser tipo OK y contener la posicion si fue correcto
    resp = socket.recv_json()
    print("RESPUESTA: ", resp)
    if resp["resp"] == "connect":
        # Establecer posicon del jugador
        jugador.act_pos(resp["pos"])
        # Cambiar estado, se puede dibujar en pantalla al jugador
        jugador.camb_dib()

        # Si es el jugador es el primero en conectarse, es quien genera aleatoreamente
        # las galletas pequeñas y la especial
        lista_galletas = pygame.sprite.RenderPlain()
        if "conf" in resp:
            # Agregar las galletas pequeñas
            rand = 5
            esp = False
            lista_g = []
            for row in range(19):
              for column in range(19):
                  if (row == 7 or row == 8) and (column == 8 or column == 9 or column == 10):
                      continue
                  else:
                      galleta = Galleta_p(yellow, 4, 4)
                      # Determinar si es la galleta especial
                      if not esp:
                          randg = random.randrange(20)
                          if randg == 0:
                              galleta = Galleta_p(red, 4, 4)
                              print("La especial")
                              galleta.esp = True
                              esp = True

                  # Definir posicion galleta pequeña
                  galleta.rect.x = (30*column+6)+26
                  galleta.rect.y = (30*row+6)+26
                  if not pygame.sprite.spritecollide(galleta, lista_w, False):
                      if galleta.esp:
                          pos = (galleta.rect.left, galleta.rect.top)
                          print(pos)
                          if not(pos != (8, 8) and pos != (566, 8) and pos != (8, 566) and pos != (566, 566) and pos != (287, 271) and pos != (6, 306) and pos != (566, 306)):
                              esp = False
                      rect = [galleta.rect.x, galleta.rect.y, galleta.color]
                      lista_g.append(rect)
                  elif galleta.esp:
                      esp = False
                      #sprites.agregar(galleta)

            #bll = len(lista_g)
            socket.send_json({"tipo":"conf_ini", "rect_ga": lista_g})
            resp = socket.recv_json()

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
                pos_ene = resp["pos_ene"]
                print("SE CONECTARON TODOS LOS JUGADORES...")
                print("Iniciando...")

        # Agregar sprites enemigos
        index_ene = {}
        lista_e = pygame.sprite.RenderPlain()
        for enemigo in pos_ene:
            if not(enemigo == jugador.ide):
                pos_en = pos_ene[enemigo]
                en = Jugador(pacman_ene_img, enemigo)
                en.act_pos(pos_en)
                en.camb_dib()
                sprites.agregar(en)
                lista_e.add(en)
                index_ene[enemigo] = sprites.lista.index(en)
        print("ENEMIGOS: ")
        for i, ene in enumerate(lista_e):
            print (i+1, ". ", ene.ide)

        # Agregar mapa de galletas
        lista_g = resp["conf_ini"]
        for rect in lista_g:
            galleta = Galleta_p(rect[2], 4, 4)
            galleta.rect.x = rect[0]
            galleta.rect.y = rect[1]
            if rect[2] == list(red):
                galleta.esp = True
            lista_galletas.add(galleta)
            sprites.agregar(galleta)

        bll = len(lista_galletas)

        # Iniciar graficos
        pygame.init()
        screen = pygame.display.set_mode([606, 606])
        pygame.display.set_caption('Pacman ' + ide)
        background = pygame.Surface(screen.get_size())
        background.fill(black)
        clock = pygame.time.Clock()
        pygame.font.init()
        font = pygame.font.Font("freesansbold.ttf", 24)
        win = False
        score = 0

    else:
        print("OCURRIO UN ERROR AL CONECTARSE")
        exit()


    while not win:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN and not(jugador.elim):
                if event.key == pygame.K_LEFT:
                    # Verificar si puede moverse a la izquierda
                    rect_a = jugador.rect
                    jugador.rect.left = jugador.rect.left - 30
                    if not pygame.sprite.spritecollide(jugador, lista_w, False):
                        sprites.actualizar(jugador)
                        socket.send_json({"tipo":"movimiento", "pos_act": jugador.ret_pos(), "id":ide})
                        resp = socket.recv_json()
                    else:
                        jugador.rect.left = jugador.rect.left + 30
                        sprites.actualizar(jugador)
                if event.key == pygame.K_RIGHT:
                    # Verificar si puede moverse a la derecha
                    rect_a = jugador.rect
                    jugador.rect.right = jugador.rect.right + 30
                    if not pygame.sprite.spritecollide(jugador, lista_w, False):
                        sprites.actualizar(jugador)
                        socket.send_json({"tipo":"movimiento", "pos_act": jugador.ret_pos(), "id":ide})
                        resp = socket.recv_json()
                    else:
                        jugador.rect.right = jugador.rect.right - 30
                        sprites.actualizar(jugador)

                if event.key == pygame.K_UP:
                    # Verificar si puede moverse arriba
                    rect_a = jugador.rect
                    jugador.rect.top = jugador.rect.top - 30
                    if not pygame.sprite.spritecollide(jugador, lista_w, False):
                        sprites.actualizar(jugador)
                        socket.send_json({"tipo":"movimiento", "pos_act": jugador.ret_pos(), "id":ide})
                        resp = socket.recv_json()
                    else:
                        jugador.rect.top = jugador.rect.top + 30
                if event.key == pygame.K_DOWN:
                    rect_a = jugador.rect
                    jugador.rect.bottom = jugador.rect.bottom + 30
                    if not pygame.sprite.spritecollide(jugador, lista_w, False):
                        sprites.actualizar(jugador)
                        socket.send_json({"tipo":"movimiento", "pos_act": jugador.ret_pos(), "id":ide})
                        resp = socket.recv_json()
                    else:
                        jugador.rect.bottom = jugador.rect.bottom - 30

        # En caso de comer galletas
        if not jugador.conv:
            comidas_p = pygame.sprite.spritecollide(jugador, lista_galletas, True)
            if len(comidas_p) > 0:
                obj = comidas_p[0]
                rect = (obj.rect.left, obj.rect.top, obj.rect.width, obj.rect.height)
                socket.send_json({"tipo":"eat", "rect": rect, "esp": obj.esp, "id": ide})
                r = socket.recv_json()
                #sprites.lista.pop(index)
                score = score + 1

        # En caso de comer al enemigo
        if jugador.eneconv:
            comidos_e = pygame.sprite.spritecollide(jugador, lista_e, True)
            if len(comidos_e) > 0:
                obj_e = comidos_e[0]
                id_en = obj_e.ide
                socket.send_json({"tipo":"eat-ene", "id_en": id_en, "ide": ide})
                r = socket.recv_json()

        # Pintar pantalla de negro
        screen.fill(black)

        # Actualizar ---------------------------------------
        socket.send_json({"tipo": "act", "id":ide})
        resp = socket.recv_json()

        if not(resp["resp"] == "GANO"):
            # Convertir a fantasmas de ser el caso
            if resp["convertir"]:
                jugador.conv = True
                jugador.camb_img(fantasma_img)

            # Actualizar enemigos
            pos_ene = resp["pos_ene"]
            for enemigo in pos_ene:
                sprites.lista[index_ene[enemigo]].rect.left = pos_ene[enemigo][0]
                sprites.lista[index_ene[enemigo]].rect.top = pos_ene[enemigo][1]
                if not(resp["convertir"]):
                    if resp["conv_t"]:
                        jugador.eneconv = True
                        sprites.lista[index_ene[enemigo]].conv = True
                        sprites.lista[index_ene[enemigo]].camb_img(fantasma_ene_img)

            # Actualizar galletas
            elim_gall = resp["galletas"]
            for galleta in elim_gall:
                rect_g = pygame.Rect(galleta)
                for sprt in sprites.lista:
                    if sprt.rect == rect_g:
                        i = sprites.lista.index(sprt)
                        sprites.lista[i].dib = False
                        sprites.lista[i].rect.left = -50
                        sprites.lista[i].rect.top = -50

            # Verificar eliminados:
            if resp["elim"]:
                #sprites.lista.remove(jugador)
                jugador.elim = True

            # Eliminar enemigos
            if resp["elim_e"] != None and resp["elim_e"] != jugador.ide:
                sprites.eliminar(resp["elim_e"])

            sprites.dibujar(screen)
            text = font.render("Score: "+str(score)+"/"+str(bll), True, red)
            if not jugador.elim:
                screen.blit(text, [10, 10])
            else:
                text_e = font.render("ESTAS ELIMINADO. ESPERA", True, red)
                screen.blit(text_e, [10, 10])

            pygame.display.flip()

            clock.tick(10)
        else:
            if not jugador.elim:
                text_w = font.render("FELICITACIONES GANASTE", True, red)
                screen.blit(text_w, [10, 303])
            else:
                text_l = font.render("LASTIMA. PERDISTE", True, red)
                screen.blit(text_l, [10, 303])

            pygame.display.flip()
            clock.tick(0.4)
            win = True

def main():
    startGame()
    pygame.quit()

if __name__ == '__main__':
    main()
