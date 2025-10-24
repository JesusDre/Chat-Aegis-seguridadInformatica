import socket        # Para conectar dos computadoras
import threading     # Para hacer varias cosas al mismo tiempo

# Función para escuchar mensajes del servidor
def escuchar_servidor(socket_cliente):
    while True:
        mensaje = socket_cliente.recv(1024).decode('utf-8')  # Recibe mensaje
        if not mensaje:  # Si no hay mensaje, se cerró la conexión
            break
        print(f"\nServidor: {mensaje}")  # Muestra el mensaje

# --- CONFIGURACIÓN DEL CLIENTE ---
socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Crea el socket (canal de comunicación)

socket_cliente.connect(('127.0.0.1', 5000))
# Se conecta al servidor en la misma computadora

print("Conectado al servidor...")

# --- HILO PARA ESCUCHAR AL SERVIDOR ---
hilo_escucha = threading.Thread(target=escuchar_servidor, args=(socket_cliente,))
hilo_escucha.start()  # Inicia el hilo para escuchar

# --- ENVIAR MENSAJES AL SERVIDOR ---
while True:
    mensaje = input("Tú: ")  # Escribe tu mensaje
    socket_cliente.send(mensaje.encode('utf-8'))  # Envía el mensaje