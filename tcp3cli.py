import selectors
import socket
import sys
import signal


#definicion de funciones


def compParam(): #comprobacion de parametros de entrada

	if len(sys.argv)==3: #deteccion de solicitud de conexion tcp
		print("ESTE CLIENTE SE ESTÁ EJECUTANDO EN TCP")
		print("--------------------------------------------------------------------------\n")
		return "tcp"

	elif len(sys.argv)==4: #deteccion de solicitud de conexion udp
		print("ESTE CLIENTE SE ESTÁ EJECUTANDO EN UDP")
		print("--------------------------------------------------------------------------\n")
		return "udp"

	else:	#deteccion de error en la invocacion del cliente
		print("Sintaxis correcta: tcp3cli ip_address port_numer [-u]") #aviso para entrada incorrecta
		sys.exit() #cierre de programa


def controlC(signal,frame): #regulacion de control+C

		print("\nSe ha cerrado este cliente")

		if metodo=="tcp":
			este_cliente.unregister(conexion)
			conexion.close() #fin de la conexion tcp
			este_cliente.close() #cierre del cliente tcp
			exit()

		elif metodo=="udp":		
			socket_udp.close() #cierre del cliente udp
			exit()



#codigo principal

signal.signal(signal.SIGINT,controlC)

#inicilizacion de parametros
metodo = compParam() #eleccion entre tcp o udp
mens = "Introduce una serie de números: "
dir_servidor = (sys.argv[1],int(sys.argv[2]))
entrada = []

#codigo para tcp
if metodo=="tcp":

	#inicializacion de parametros tcp	
	este_cliente = selectors.DefaultSelector()
	enviar = True

	#creacion del socket tcp
	socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	socket_tcp.connect(dir_servidor)


	#registro del socket en el selector	
	este_cliente.register(
		socket_tcp,
		selectors.EVENT_READ | selectors.EVENT_WRITE,
	)

	while True:

		envio = "" #inicializacion del mensaje a enviar

		for key, mask in este_cliente.select(timeout=0):

			conexion = key.fileobj #establecimiento de la conexion tcp

			#codigo para el envio del mensaje a traves de la conexion tcp 
			if enviar:
				entrada = [n for n in input(mens).split()] #lectura por teclado de la entrada
				if int(entrada[0])==0: #deteccion de la solicitud de cierre del cliente
					print ("Se ha cerrado este cliente")
					este_cliente.unregister(conexion) #borrado del cliente del registro del selector
					conexion.close() #cierre de la conexion
					este_cliente.close() #cierre del cliente
					exit() #cierre del programa

				else: #envio de la entrada
					for i in entrada: #construccion del mensaje a enviar
						envio = envio+str(i)+" "
					socket_tcp.sendall(envio.encode("utf-8")) #envio del mensaje
					enviar = False

			#codigo para la lectura de la respuesta recibida a traves de la conexion tcp
			else:
				acum = conexion.recv(1024).decode("utf-8") #lectura de la respuesta recibida
				if acum:
					print ("Valores enviados:", end=" ")
					for i in entrada:
						print(i, end=" ")
					print("| ACUMULADOR:",acum,"\n") #impresion final
					enviar = True

#codigo para udp
elif metodo=="udp":

	#creacion del socket udp
	socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	while True:

		envio = "" #inicializacion del mensaje a enviar
		entrada = [n for n in input(mens).split()] #lectura por teclado de la entrada

		if int(entrada[0])==0: #deteccion de la solicitud de cierre del cliente
			socket_udp.sendto("end".encode("utf-8"), dir_servidor)
			print ("Se ha cerrado este cliente")
			socket_udp.close() #cierre de la conexion
			exit() #cierre del programa

		else: #envio de la entrada
			for i in entrada: #construccion del mensaje a enviar
				envio=envio+str(i)+" "
			socket_udp.sendto(envio.encode("utf-8"), dir_servidor) #envio del mensaje
			acum, servidor = socket_udp.recvfrom(1024) #lectura de la respuesta recibida
			if acum:
				print ("Valores enviados:", end=" ")	
				for i in entrada:
					print(i, end=" ")
				print("| ACUMULADOR UDP:",acum.decode("utf-8"),"\n") #impresion final
