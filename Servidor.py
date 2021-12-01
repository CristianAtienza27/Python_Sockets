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
        global turno, jugadores, numJugadores, tiempo, jugadoresOrdenados, cad, listaPreguntas

        while self.logueado == False:
            datos = self.socket.recv(1024).decode().split(';')

            if datos[0] == 'login':
                if(login(datos[1], datos[2])):
                    self.socket.send("True".encode())
                    self.email = datos[1]
                    self.logueado = True
                else:
                    self.socket.send("False".encode())
            elif datos[0] == 'registro':
                if(registro(datos[1], datos[2])):
                    self.socket.send("True".encode())
            else:
                self.socket.send("False".encode())
        
        self.nombre = self.socket.recv(1024).decode() 

        turno.acquire() 

        numJugadores = numJugadores + 1

        tiempo = tiempo + 1

        while numJugadores != 2:
            pass

        print('¡Comienza la partida!')
        sleep(2)

        for pregunta in self.preguntas:
                
            self.socket.send(str('P;' + (pregunta[1] + '\n' + pregunta[2] + '\n' + pregunta[3] + '\n' + pregunta[4]+ '\n' + pregunta[5])).encode())
            if comprobarRespuesta(pregunta[0], self.socket.recv(1024).decode()):
                self.socket.send('Acierto'.encode())   
                self.aciertos += 1
            else:
                self.socket.send('Fallo'.encode())  

        self.socket.send(str('FT;>>> Puntuación: ' + str(self.aciertos) + ' pts\nEsperando a que acaben el resto de jugadores...').encode())

        jugadores.__setitem__(self.email, self.aciertos)

        numJugadores = numJugadores - 1

        if numJugadores == 0:

            mutex.acquire()

            if (os.path.isfile('./clasificacion.txt') == False):
                file = Path('./clasificacion.txt')
                file.touch(exist_ok=True)

            jugadores = sorted(jugadores.items(), key=operator.itemgetter(1))

            clasificacion = open("./clasificacion.txt","a")

            for jug in enumerate(jugadores):
                clasificacion.write(jug[1][0] + ';' + str(jug[1][1]) +  "\n") 
                cad += jug[1][0] + ' ' + str(jug[1][1]) + '\n'               

            clasificacion.close()

            mostrarRanking(self.email, self.aciertos)

            mutex.release()

            sleep(1)

        while numJugadores != 0:
            pass

        sleep(tiempo)
        
        self.socket.send(str('FP;\n>>> Fin de la partida <<<\n' + cad).encode())

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

def mostrarRanking(emailJugador: str, aciertos: int):
    clasificacion = open("./clasificacion.txt", "r")
    jugPuntos = {}
    pos = 0

    for linea in clasificacion:
        datos = linea.split(';')
        jugPuntos.__setitem__(datos[0], datos[1])
    
    clasificacion.close()

    jugPuntos = sorted(jugPuntos.items(), key=operator.itemgetter(1), reverse=True)

    for jug in enumerate(jugPuntos):
        if emailJugador == jug[1][0]:
            jug[1][1] = int(jug[1][1] + int(aciertos))

    for jug in enumerate(jugPuntos):
        pos += 1
        print(str(pos) + ') ' + jug[1][0] + ' ' + jug[1][1])


turno = Semaphore(2)
mutex = Lock()
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("",9004))
server.listen(1)

jugadores = {}
jugadoresOrdenados = {}
cad = ''
numJugadores = 0
tiempo = 0
listaPreguntas = cargarPreguntas()

while True:
    socket_cliente, datos_cliente = server.accept()
    jugador = Trivial(socket_cliente, datos_cliente, listaPreguntas)
    jugador.start()



    



