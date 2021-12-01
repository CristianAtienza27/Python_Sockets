import socket, os
from pathlib import Path
from time import sleep
import re

def comprobarEmail(email):
    expresion_regular = "(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"
    return re.match(expresion_regular, email)

def login():
    global salir, logueado, server

    email = input('Login\nEmail: ')
    password = input('Password: ')

    server.send(('login;' + email + ';' + password).encode())

    respuesta = server.recv(1024).decode()

    if respuesta == 'True':
        print('Logueado con éxito')
        logueado = True
    else:
        print('Credenciales incorrectas')

    # fichero = open("./usuarios.txt","r")

    # for lineas in fichero:
    #     datos = lineas.split(';')
        
    #     if email == datos[0] and password == datos[1].strip():
    #         fichero.close()
    #         print('¡Logueado con éxito!')
    #         logueado = True
    #         sleep(2)
    #         os.system('cls')
    #         nickname = input('Introduzca un nickname: ')
    #         print('Esperando al resto de jugadores...')
    #         #Entrada servidor

    #         break

    # if not logueado:
    #     fichero.close()
    #     print('Credenciales incorrectas, Intente otra vez')
    sleep(1)
    os.system('cls')

def registro():

    existe = False

    if (os.path.isfile('./usuarios.txt') == False):
        file = Path('./usuarios.txt')
        file.touch(exist_ok=True)

    email = input('Nuevo usuario\nEmail: ')
    password = input('Password: ')

    if comprobarEmail(email):
        server.send('registro;' + email + ';'+ password)
        respuesta = server.recv(1024).decode()

        if respuesta == 'True':
            print('Usuario registrado satisfactoriamente')
        else:
            print('El email proporcionado ya existe')
        
        # fichero = open("./usuarios.txt",'r')

        # for lineas in fichero:
        #     datos = lineas.split(';')

        #     if datos[0] == email:
        #         print('El email ya existe, intente con otro email')
        #         existe = True
        #         fichero.close()
        #         sleep(2)
        #         os.system('cls')
        #         break
        #     else:
        #         existe = False

        # if not existe:
        #     fichero = open("./usuarios.txt",'a')
        #     fichero.write(email + ';' + password)
        #     fichero.write("\n")
        #     print('Usuario registrado con éxito')
        #     existe = True
        #     fichero.close()
        #     sleep(2)
    else:
        print('Formato de email no válido')
    
    sleep(2)
        
    os.system('cls')

salir = False
logueado = False

server = socket.socket()
server.connect(("localhost", 9004))

while not logueado and not salir:
    print('< MENÚ PRINCIPAL >\n1.) Login\2.) Registrarse\n')
    opcion = input('Introduce una opción: ')

    if opcion == '1':
        login()
    elif opcion == '2':
        registro()
    elif opcion == '*':
        salir = True
        print('Saliendo...')
        sleep(2)
        os.system('cls')
    else:
        print('Opción incorrecta')

nickname = input('Introduce tu nickname: >>>')
server.send(nickname.encode())

while not salir:

    enunciado = server.recv(1024).decode().split(';')

    if enunciado[0] == 'P':
        print(enunciado[1])
    # Contesta y envia la respuesta
        respuesta = input("Respuesta >> ")
    # Se envía la respuesta al servidor
        server.send(respuesta.upper().encode())
    # Comprueba acierto
        acierto = server.recv(1024).decode()
        print(acierto)
        sleep(2)
        os.system('cls')
    elif enunciado[0] == 'FT':
        print(enunciado[1])
    elif enunciado[0] == 'FP':
        print(enunciado[1])
        salir = True
        break

server.close()

    



     

     

  
   
     
        


