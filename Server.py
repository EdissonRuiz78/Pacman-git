import zmq
import sys
import json
import random
import threading
import time

# Posiciones establecidas para los jugadores
# Se establece 7 posiciones, siendo el recomendable 4. (Saturación imagen)
posiciones_jug = [(8, 8), (566, 8), (8, 566), (566, 566), (287, 271), (6, 306), (566, 306)]

class Convert():
    def __init__(self):
        self.convertir = [False, None]
        self.reconv = False

    def camb_est(self, bol, ide):
        self.convertir = [bol, ide]

def cambio(c):
    print("Comienzan fantasmas")
    time.sleep(15)
    print("A reconvertirse")
    c.reconv = True


def main():
    if len(sys.argv) != 2:
        print("Debe definir cantidad de jugadores")
        exit()

    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:4444")

    print("Iniciando servidor")
    cant_jug = int(sys.argv[1]) # Suministrado desde consola

    # Variable para jugadores
    posiciones_t = posiciones_jug[:cant_jug] # Extraer n posiciones para cant_jug
    ID = []
    posiciones = {} # Diccionario que almacena las posicones, la llave es el id del jugador
    jug_cont = 0 # Contador para controlar cuantos jugadores se conectaron

    # Variables para controlar cambios de galletas
    indx_g = []
    conf_ini = []

    # Variables para controlar conversion a fantasmas
    c = Convert()
    cant_conv = 0

    # Variables para controlar eliminacion de jugador
    eliminar = [False, None]
    cant_inf = 0

    # Variables para controlar los puntos
    cant_ga = 0
    puntos_p = 0

    # Variable para continuar ciclo
    win = False
    cant_w = 0 # Jugadores informados de la victoria
    # Posiciones de Galletas:
    while not win:
        # Recibir mensaje
        msg = socket.recv_json()
        if msg["tipo"] == "connect" and jug_cont < cant_jug:
            print("Recibi una conexión")

            # Darle una posicion al jugador que se conecta
            index = random.randrange(len(posiciones_t))
            pos = posiciones_t[index]
            del posiciones_t[index]
            jug_cont = jug_cont + 1

            # Almacener el id del jugador
            ID.append(msg["id"])

            # Almacenar posicion del jugador en Diccionario
            posiciones[msg["id"]] = pos

            resp = {"resp":"connect", "pos":pos}
            if len(posiciones) == 1:
                resp["conf"] =  "map"

            socket.send_json(resp)

        elif msg["tipo"] == "conf_ini":
            conf_ini = msg["rect_ga"]
            socket.send_json({"resp": "Si"})

        # Cuando un jugador desea iniciar pero no se han conectado todos los jugadores
        elif msg["tipo"] == "init":
            if not(jug_cont == cant_jug):
                socket.send_json({"resp":"No", "cant": jug_cont})
            else:
                cant_ga = len(conf_ini) # Cantidad de galletas que serán comidas
                puntos_p = cant_jug + cant_ga # Puntos totales que hay que alcanzar
                socket.send_json({"resp":"Si", "cant": jug_cont, "pos_ene": posiciones, "conf_ini": conf_ini})

        elif msg["tipo"] == "movimiento":
            posiciones[msg["id"]] = msg["pos_act"]
            socket.send_json({"resp": "OK"})

        elif msg["tipo"] == "eat":
            # Agregar a una lista, cuando se actualice, se ordena que se elimine
            indx_g.append(msg["rect"])
            puntos_p = puntos_p - 1
            socket.send_json({"resp": "OK"})
            # Si se comio la galleta especial
            if msg["esp"]:
                c.camb_est(True, msg["id"])
                t = threading.Thread(target=cambio, args=(c, ))
                t.start()

        elif msg["tipo"] == "eat-ene":
            eliminar = [True, msg["id_en"]]
            print("Eliminado {0} por {1}".format(msg["id_en"], msg["ide"]))
            puntos_p = puntos_p - 1
            socket.send_json({"resp": "OK"})

        elif msg["tipo"] == "act":
            #print("POSCIONES: ID {0} POS {1}".format(msg["id"], posiciones[msg["id"]]))
             # Solo puede quedar un punto por hacer: el jugador sobreviviente
            if not(puntos_p == 1):
                # Actualizar posicones
                if msg["id"] in posiciones:
                    temp = posiciones[msg["id"]]
                    posiciones.pop(msg["id"])

                    # Si alguien comio la galleta especial:
                    if c.convertir[0] and not(c.convertir[1] == msg["id"]):
                        conv = True
                        cant_conv = cant_conv + 1
                    else:
                        conv = False

                    # Si eliminan a jugador
                    if eliminar[0] and (eliminar[1] == msg["id"]):
                        elim = True
                        cant_inf = cant_inf + 1
                    else:
                        elim = False

                    socket.send_json({"resp": "OK",
                                      "pos_ene": posiciones,
                                      "galletas":indx_g,
                                      "convertir": conv,
                                      "conv_t": c.convertir[0],
                                      "reconv": c.reconv,
                                      "elim": elim,
                                      "elim_e": eliminar[1],
                                      })
                    if not elim:
                        posiciones[msg["id"]] = temp

                    if cant_conv == cant_jug:
                        c.camb_est(False, None)
                        cant_conv = 0
                    if cant_inf == cant_jug:
                        eliminar, cant_inf = [False, None], 0
                else:
                    socket.send_json({"resp": "eliminado"})
            else:
                socket.send_json({"resp": "GANO"})
                cant_w = cant_w + 1

                if cant_w == cant_jug:
                    win = True

if __name__ == '__main__':
    main()
