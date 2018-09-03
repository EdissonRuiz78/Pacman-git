import zmq
import sys
import json
import random

# Posiciones establecidas para los jugadores
# Se establece 7 posiciones, siendo el recomendable 4. (Saturación imagen)
posiciones_jug = [(8, 8), (566, 8), (8, 566), (566, 566), (287, 271), (6, 306), (566, 306)]

def main():
    if len(sys.argv) != 2:
        print("Debe definir cantidad de jugadores")
        exit()

    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:4444")

    print("Iniciando servidor")
    cant_jug = int(sys.argv[1]) # Suministrado desde consola

    # Cantidad de jugadores y sus posicones
    posiciones_t = posiciones_jug[:cant_jug] # Extraer n posiciones para cant_jug
    ID = []
    posiciones = {} # Diccionario que almacena las posicones, la llave es el id del jugador
    jug_cont = 0
    indx_g = []
    conf_ini = []
    convertir = [False, None]
    cant_conv = 0
    eliminar = [False, None]
    cant_inf = 0
    # Posiciones de Galletas:
    while True:
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
                socket.send_json({"resp":"Si", "cant": jug_cont, "pos_ene": posiciones, "conf_ini": conf_ini})

        elif msg["tipo"] == "movimiento":
            posiciones[msg["id"]] = msg["pos_act"]
            socket.send_json({"resp": "OK"})

        elif msg["tipo"] == "eat":
            # Agregar a una lista, cuando se actualice, se ordena que se elimine
            indx_g.append(msg["rect"])
            socket.send_json({"resp": "OK"})
            # Si se comio la galleta especial
            if msg["esp"]:
                convertir = [True, msg["id"]]

        elif msg["tipo"] == "eat-ene":
            eliminar = [True, msg["id_en"]]
            socket.send_json({"resp": "OK"})

        elif msg["tipo"] == "act":
            # Actualizar posicones
            temp = posiciones[msg["id"]]
            posiciones.pop(msg["id"])

            # Si alguien comio la galleta especial:
            if convertir[0] and not(convertir[1] == msg["id"]):
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
                              "conv_t": convertir[0],
                              "elim": elim,
                              "elim_e": eliminar[1],
                              })

            # Eliminar galletas consumidas
            posiciones[msg["id"]] = temp

            if cant_conv == cant_jug:
                convertir, cant_conv = [False, None], 0
            if cant_inf == cant_jug:
                eliminar, cant_inf = [False, None], 0


if __name__ == '__main__':
    main()
