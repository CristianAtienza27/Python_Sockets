from threading import Thread, Semaphore, Lock
import socket
import random
import operator
import os, os.path
from pathlib import Path
from time import sleep 

class Trivial(Thread):
    def __init__(self,socket_cliente, datos_cliente, preguntas):
        Thread.__init__(self)
        self.socket = socket_cliente
        self.datos = datos_cliente
        self.email = ''
        self.nombre= ''
        self.logueado = False
        self.aciertos = 0
        self.preguntas = preguntas      

    def run(self):
        global turno, jugadores, numJugadores, tiempo, jugadoresOrdenados, cadena, listaPreguntas

        #El servidor recibe la opción elegida, email y contraseña del cliente
        while self.logueado == False:
            datos = self.socket.recv(1024).decode().split(';')

            #login
            if datos[0] == 'login':
                if(login(datos[1], datos[2])):
                    self.socket.send("True".encode())
                    self.email = datos[1]
                    self.logueado = True
                else:
                    self.socket.send("False".encode())
            #registro
            elif datos[0] == 'registro':
                if not registro(datos[1], datos[2]):
                    self.socket.send("True".encode())
                else:
                    self.socket.send("False".encode())
            else:
                self.socket.send("False".encode())
        
        # recibimos nickname del cliente
        self.nombre = self.socket.recv(1024).decode() 

        #ocupamos un semáforo 
        turno.acquire() 

        numJugadores = numJugadores + 1

        tiempo = tiempo + 1

        #mientras los jugadores sean distintos de 4 no empieza la partida
        while numJugadores != 2:
            pass

        print('¡Comienza la partida!')
        sleep(2)

        #envía las 5 preguntas de una en una al cliente (ver método cargar preguntas)
        for pregunta in self.preguntas:
                
            self.socket.send(str('P;' + (pregunta[1] + '\n' + pregunta[2] + '\n' + pregunta[3] + '\n' + pregunta[4]+ '\n' + pregunta[5])).encode())
            
            #recibimos la respuesta y la comprobamos si es correcta o no (ver método comprobarRespuesta)
            if comprobarRespuesta(pregunta[0], self.socket.recv(1024).decode()):
                self.socket.send('Acierto'.encode())   
                self.aciertos += 1
            else:
                self.socket.send('Fallo'.encode())  

        #una vez acabado el turno del jugador, se le envía su puntuación y lo mantenemos a la espera de que terminen los 4
        self.socket.send(str('FT;>>> Puntuación: ' + str(self.aciertos) + ' pts\nEsperando a que acaben el resto de jugadores...').encode())

        #almacenamos su email y su numero de aciertos
        jugadores.__setitem__(self.email, self.aciertos)

        numJugadores = numJugadores - 1

        cadena = ""
        jugadoresOrdenados = list()
        clasDic = {}

        #cuando terminamos la partida, es decir, cuando el número de jugadores sea 0
        if numJugadores == 0:
            
            #usamos mutex para proteger el acceso al fichero
            mutex.acquire()

            #creamos el fichero para almacenar la clasificación si no existe
            if (os.path.isfile('./clasificacion.txt') == False):
                file = Path('./clasificacion.txt')
                file.touch(exist_ok=True)

            #Ordenmos los jugadores por puntuación
            jugadoresOrdenados = sorted(jugadores.items(), key=operator.itemgetter(1), reverse=True)

            clasificacion = open("./clasificacion.txt","r")
            
            #almacenamos en un diccionario todos los registros de la clasificacion
            for linea in clasificacion:
                datos = linea.split(";")
                clasDic.__setitem__(datos[0], datos[1])

            clasificacion.close()
            keys = clasDic.keys()

            #recorremos la lista de jugadores ordenados
            for jugador in enumerate(jugadoresOrdenados):
                
                #si el jugadador aparece en la lista de claves se le suma los puntos actuales
                # y se le asigna el nuevo valor en su posición, y si no, lo insertamos en el diccionario
                if (jugador[1][0] in keys):
                    valor = int(clasDic[jugador[1][0]]) + int(jugadores[jugador[1][0]])
                    clasDic[jugador[1][0]] = valor
                else:
                    clasDic.__setitem__(jugador[1][0], jugadores[jugador[1][0]])

                cadena += str(jugador[1][0]) + ' ' + str(jugador[1][1]) + "\n"

            general = open("./clasificacion.txt", "w")
            
            #escribimos en el fichero de la clasificacion toda la clasificacion actualizada con
            #las últimas puntuaciones
            for key, value in clasDic.items():
                jugador = str(key) + ";" + str(value)
                general.write(str(jugador) + "\n")

            general.close() 

            mostrarClasificacionGen()              

            mutex.release()

            sleep(1)

        #esperamos a que no haya jugadores 
        while numJugadores != 0:
            pass

        sleep(tiempo)
        
        #enviamos a los jugadores, cómo han quedado en la partida
        self.socket.send(str('FP;\n>>> Fin de la partida <<<\n' + str(cadena)).encode())

        turno.release()

        self.socket.close()

def login(email, password):
    logueado = False
    usuarios = open("./usuarios.txt", 'r')

    for linea in usuarios:

        datos = linea.split(';')

        if datos[0] == email and datos[1].strip() == password:
            logueado = True
            
    usuarios.close()

    return logueado

def registro(email, password):

    existe = False

    if (os.path.isfile('./usuarios.txt') == False):
        file = Path('./usuarios.txt')
        file.touch(exist_ok=True)
    
    usuarios = open('./usuarios.txt')

    for lineas in usuarios:
            datos = lineas.split(';')

            if datos[0] == email:
                print('El email ya existe, intente con otro email')
                existe = True
                usuarios.close()
                sleep(2)
                    
                break
            else:
                existe = False

    if not existe:
        usuarios = open("./usuarios.txt",'a')
        usuarios.write(email + ';' + password)
        usuarios.write("\n")
        print('Usuario registrado con éxito')
        existe = False
        usuarios.close()
        sleep(2)
    
    return existe

def cargarPreguntas():
    preguntas = []
    preguntasElegidas = []
    fichero = open("preguntas.txt","r")

    for lineas in fichero:
        datos = lineas.split(';')

        preguntas.append(datos)
    
    fichero.close()

    for i in range(0,5):
        pregunta = random.choice(preguntas)
        preguntas.remove(pregunta)
        preguntasElegidas.append(pregunta)

    return preguntasElegidas

def comprobarRespuesta(numPregunta, resp):

    fichero = open("respuestas.txt", 'r')

    for lineas in fichero:
        datos = lineas.split(';')

        if numPregunta == datos[0] and resp == datos[1].strip():
            fichero.close()
            return True

    fichero.close()
    return False

def mostrarClasificacionGen():

    clasificacion = open("./clasificacion.txt", "r")
    jugadores = {}

    for l in clasificacion:
        p = l.split(";")
        jugadores.__setitem__(p[0], p[1])

    clasificacion.close()

    jugadoresOrdenados = sorted(jugadores.items(), key=operator.itemgetter(1), reverse=True)
    pos = 0

    for jugador in enumerate(jugadoresOrdenados):
        pos += 1
        print(str(pos) + ') ' + "{}".format(jugador[1][0]) + ' ' + "{}".format(jugadores[jugador[1][0]]))


turno = Semaphore(2)
mutex = Lock()
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("",9004))
server.listen(1)

jugadores = {}
jugadoresOrdenados = {}
numJugadores = 0
cadena = ''
tiempo = 0
listaPreguntas = cargarPreguntas()

while True:
    socket_cliente, datos_cliente = server.accept()
    jugador = Trivial(socket_cliente, datos_cliente, listaPreguntas)
    jugador.start()



    



