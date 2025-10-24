import socket          # Para comunicación entre computadoras
import threading       # Para ejecutar tareas en paralelo
from cryptography.hazmat.primitives.asymmetric import rsa  # Para claves RSA
from cryptography.hazmat.primitives import serialization   # Para guardar/cargar claves

# --- Generación de claves RSA ---
# El servidor genera su par de claves (privada y pública)
clave_privada = rsa.generate_private_key(public_exponent=65537, key_size=2048)
clave_publica = clave_privada.public_key()

# Exporta la clave pública para compartirla con el cliente
clave_publica_pem = clave_publica.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# Función para escuchar los mensajes del cliente (sin firma/verificación)
def escuchar_cliente(conexion, clave_publica_cliente=None):
    while True:
        datos = conexion.recv(4096)  # Recibe datos en bytes
        if not datos:
            break
        try:
            mensaje = datos.decode('utf-8')
        except Exception:
            print("Formato de mensaje incorrecto.")
            continue

        # Muestra el mensaje recibido (sin verificación criptográfica)
        print(f"\nCliente: {mensaje}")

# --- CONFIGURACIÓN DEL SERVIDOR ---
socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_servidor.bind(('0.0.0.0', 5000))
socket_servidor.listen(1)
print("Esperando conexión...")

conexion, direccion = socket_servidor.accept()
print(f"Conectado con {direccion}")

# Envía la clave pública del servidor al cliente (mantener intercambio de claves sin firmas)
conexion.send(clave_publica_pem)

# Recibe la clave pública del cliente (opcional, útil para cifrado futuro)
clave_publica_cliente_pem = conexion.recv(4096)
try:
    clave_publica_cliente = serialization.load_pem_public_key(clave_publica_cliente_pem)
except Exception:
    clave_publica_cliente = None

# Crea un hilo para escuchar los mensajes del cliente
hilo_escucha = threading.Thread(target=escuchar_cliente, args=(conexion, clave_publica_cliente))
hilo_escucha.start()

# Bucle para enviar mensajes al cliente (sin firma)
while True:
    mensaje = input("Tú: ")
    conexion.send(mensaje.encode('utf-8'))