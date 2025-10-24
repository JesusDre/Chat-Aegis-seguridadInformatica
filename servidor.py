import socket        # Para comunicación entre computadoras
import threading     # Para hacer varias cosas al mismo tiempo

# Función para escuchar mensajes del cliente
def escuchar_cliente(conexion):
    while True:
        mensaje = conexion.recv(1024).decode('utf-8')  # Recibe mensaje
        if not mensaje:  # Si no hay mensaje, el cliente se desconectó
            break
        print(f"\nCliente: {mensaje}")  # Muestra el mensaje

# --- CONFIGURACIÓN DEL SERVIDOR ---
socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Crea el socket (canal de comunicación)

socket_servidor.bind(('0.0.0.0', 5000))
# Asigna dirección IP y puerto

socket_servidor.listen(1)
# Espera conexiones

print("Esperando conexión...")

conexion, direccion = socket_servidor.accept()
# Espera a que un cliente se conecte
print(f"Conectado con {direccion}")

# --- HILO PARA ESCUCHAR AL CLIENTE ---
hilo_escucha = threading.Thread(target=escuchar_cliente, args=(conexion,))
hilo_escucha.start()  # Inicia el hilo para escuchar

# --- ENVIAR MENSAJES AL CLIENTE ---
while True:
    mensaje = input("Tú: ")             # Escribe tu mensaje
    conexion.send(mensaje.encode('utf-8'))  # Envía el mensaje