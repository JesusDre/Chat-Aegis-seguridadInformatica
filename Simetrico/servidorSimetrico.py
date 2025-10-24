import socket          # Importa la librería para comunicación entre computadoras
import threading       # Importa la librería para ejecutar tareas en paralelo

# Función que escucha los mensajes del cliente (sin verificación HMAC)
def escuchar_cliente(conexion):
    while True:
        datos = conexion.recv(2048).decode('utf-8')  # Recibe datos del cliente
        if not datos:  # Si no hay datos, termina el ciclo
            break
        # Ahora solo mostramos el mensaje recibido
        print(f"\nCliente: {datos}")

# --- CONFIGURACIÓN DEL SERVIDOR ---
socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Crea el socket del servidor
socket_servidor.bind(('0.0.0.0', 5000))  # Asigna la dirección IP y el puerto
socket_servidor.listen(1)  # Espera una conexión entrante
print("Esperando conexión...")  # Mensaje informativo

conexion, direccion = socket_servidor.accept()  # Acepta la conexión del cliente
print(f"Conectado con {direccion}")  # Muestra la dirección del cliente conectado

# Crea un hilo para escuchar los mensajes del cliente sin bloquear el envío
hilo_escucha = threading.Thread(target=escuchar_cliente, args=(conexion,))
hilo_escucha.start()  # Inicia el hilo

# Bucle para enviar mensajes al cliente (sin firma)
while True:
    mensaje = input("Tú: ")  # Pide al usuario que escriba un mensaje
    conexion.send(mensaje.encode('utf-8'))  # Envía el mensaje al cliente