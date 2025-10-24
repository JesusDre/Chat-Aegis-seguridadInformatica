import socket          # Para comunicación entre computadoras
import threading       # Para ejecutar tareas en paralelo
from cryptography.hazmat.primitives.asymmetric import rsa  # Para claves RSA
from cryptography.hazmat.primitives import serialization   # Para guardar/cargar claves

# --- Generación de claves RSA ---
# El cliente genera su par de claves (privada y pública)
clave_privada = rsa.generate_private_key(public_exponent=65537, key_size=2048)
clave_publica = clave_privada.public_key()

# Exporta la clave pública para compartirla con el servidor
clave_publica_pem = clave_publica.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# Función para escuchar los mensajes del servidor (sin firma/verificación)
def escuchar_servidor(socket_cliente, clave_publica_servidor=None):
    while True:
        datos = socket_cliente.recv(4096)  # Recibe datos en bytes
        if not datos:
            break
        try:
            mensaje = datos.decode('utf-8')
        except Exception:
            print("Formato de mensaje incorrecto.")
            continue

        # Muestra el mensaje recibido (sin verificación criptográfica)
        print(f"\nServidor: {mensaje}")

# --- CONFIGURACIÓN DEL CLIENTE ---
socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_cliente.connect(('127.0.0.1', 5000))
print("Conectado al servidor.")

# Recibe la clave pública del servidor
clave_publica_servidor_pem = socket_cliente.recv(4096)
try:
    clave_publica_servidor = serialization.load_pem_public_key(clave_publica_servidor_pem)
except Exception:
    clave_publica_servidor = None

# Envía la clave pública del cliente al servidor
socket_cliente.send(clave_publica_pem)

# Crea un hilo para escuchar los mensajes del servidor
hilo_escucha = threading.Thread(target=escuchar_servidor, args=(socket_cliente, clave_publica_servidor))
hilo_escucha.start()

# Bucle para enviar mensajes al servidor (sin firma)
while True:
    mensaje = input("Tú: ")
    socket_cliente.send(mensaje.encode('utf-8'))