import selectors
import selectors
import socket
import sys


#definicion de funciones


def compParam(): #comprobacion de parametros de entrada

	if len(sys.argv)==2: #deteccion de la invocacion del servidor
		print("ESTE SERVIDOR SE ESTÁ EJECUTANDO")
		print("--------------------------------------------------------------------------\n")
		return True

	else: #deteccion de error en la invocacion del servidor
		print("Sintaxis correcta: tcp3ser port_numer") #aviso para entrada incorrecta
		sys.exit() #cierre de programa


def acumulador(acum, mens, puerto, tcp): #calculo del acumulador

	print ("--------------------------------------------------------------------------")
	print ("Cliente del puerto",puerto)

	for i in mens:
		print("Valor recibido: ",i, end=" ")
		acum=acum+int(i) #calculo del acumulador
		if tcp:
			print("| ACUMULADOR:",acum) #impresion del resultado final

		else:
			print("| ACUMULADOR UDP:",acum) #impresion del resultado final 
						
	print("--------------------------------------------------------------------------\n")

	return acum


def read(conexion, mask): #lectura del mensaje y envio de la respuesta a traves de una conexion tcp

	dir_cliente = conexion.getpeername() #obtencion de la direccion del cliente
	acum = acumuladores[dir_cliente] #inicializacion del acumulador
	mens = conexion.recv(1024).decode("utf-8").strip().split() #lectura del mensaje recibido

	if mens: #lectura del mensaje y lectura de la respuesta
		acumuladores[dir_cliente] = acumulador(acum,mens,dir_cliente[1],True) #calculo del acumulador
		conexion.sendall(str(acumuladores[dir_cliente]).encode("utf-8")) #envio de la respuesta

	else: #cierre de la conexion
		print("Se ha cerrado la conexion con el cliente del puerto",dir_cliente[1],"\n")
		este_servidor.unregister(conexion) #borrado de la conexion del registro del selector
		conexion.close() #cierre de la conexion


def accept(s,mask): #establecimiento de una nueva conexion tcp

		nueva_conexion, dir_nuevo_cliente = servidor_tcp.accept() #establecimiento de una nueva conexion tcp
		print("Se ha establecido conexion con nuevo cliente en el puerto",dir_nuevo_cliente[1],"\n")
		acumuladores[dir_nuevo_cliente] = 0 #inicializacion del acumulador a 0
		este_servidor.register(nueva_conexion, selectors.EVENT_READ, read) #registro de la conexion en el selector


def cliente_udp(s,mask): #lectura del mensaje y envio de la respuesta a traves de una conexion udp

	mens, dir_cliente = servidor_udp.recvfrom(1024) #lectura del mensaje recibido

	if conexiones_udp.count(dir_cliente)==0: #deteccion de un nuevo cliente udp
		conexiones_udp.append(dir_cliente) #registro del cliente udp
		print("Se ha establecido conexion en udp con nuevo cliente en el puerto",dir_cliente[1],"\n")
	
	mens = mens.decode("utf-8").strip().split()

	while True:
		
		acum = acumuladores["udp"] #inicializacion del acumulador udp

		if mens==['end']: #cierre de la conexion
			print("Se ha cerrado la conexion con el cliente del puerto",dir_cliente[1],"\n")
			conexiones_udp.remove(dir_cliente) #borrado de la conexion en el registro de conexiones udp
			return

		else: #calculo del acumulador y envio de la respuesta
			acumuladores["udp"] = acumulador(acum,mens,dir_cliente[1],False) #calculo del acumulador
			servidor_udp.sendto(str(acumuladores["udp"]).encode("utf-8"), dir_cliente) #envio de la respuesta
			return



#codigo principal


if compParam(): #comprobacion de parametros de entrada

	#incializacion de parametros
	este_servidor = selectors.DefaultSelector()
	acumuladores = {}
	acumuladores["udp"] = 0
	conexiones_udp = []
	dir_servidor = ('',int(sys.argv[1]))

	#creacion del socket tcp
	servidor_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	servidor_tcp.bind(dir_servidor)
	servidor_tcp.listen(5)

	#registro del socket tcp en el selectpr
	este_servidor.register(servidor_tcp, selectors.EVENT_READ, accept)

	#creacion del socket udp
	servidor_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	servidor_udp.bind(dir_servidor)

	#registro del socket udp en el selector
	este_servidor.register(servidor_udp, selectors.EVENT_READ, cliente_udp)
	
	while True: #multiplexion
		for key, mask in este_servidor.select(timeout=-1):
			callback = key.data
			callback(key.fileobj, mask)
