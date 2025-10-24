import socket          # Para comunicación entre computadoras
import threading       # Para ejecutar tareas en paralelo
from cryptography.hazmat.primitives import hashes      # Para funciones de hash
from cryptography.hazmat.primitives.asymmetric import rsa, padding  # Para claves y firmas
from cryptography.hazmat.primitives import serialization            # Para guardar/cargar claves

# --- Generación de claves RSA ---
# El cliente genera su par de claves (privada y pública)
clave_privada = rsa.generate_private_key(public_exponent=65537, key_size=2048)
clave_publica = clave_privada.public_key()

# Exporta la clave pública para compartirla con el servidor
clave_publica_pem = clave_publica.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)


def verificar_firma(mensaje, firma, clave_publica_servidor):
    try:
        clave_publica_servidor.verify(
            firma,
            mensaje.encode('utf-8'),
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False


def escuchar_servidor(socket_cliente, clave_publica_servidor):
    while True:
        datos = socket_cliente.recv(4096)  # Recibe datos en bytes
        if not datos:
            break
        try:
            partes = datos.split(b'|||')
            mensaje = partes[0].decode('utf-8')
            firma = partes[1]
        except Exception:
            print("Formato de mensaje incorrecto.")
            continue

        # Verifica la firma con la clave pública del servidor
        if clave_publica_servidor and verificar_firma(mensaje, firma, clave_publica_servidor):
            print(f"\nServidor (verificado): {mensaje}")
        else:
            print("\n¡Advertencia! Mensaje no verificado.")


# --- CONFIGURACIÓN DEL CLIENTE ---
socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_cliente.connect(('127.0.0.1', 5000))
print("Conectado al servidor.")

# Recibe la clave pública del servidor
clave_publica_servidor_pem = socket_cliente.recv(4096)
clave_publica_servidor = None
try:
    clave_publica_servidor = serialization.load_pem_public_key(clave_publica_servidor_pem)
except Exception:
    clave_publica_servidor = None

# Envía la clave pública del cliente al servidor
socket_cliente.send(clave_publica_pem)

# Crea un hilo para escuchar los mensajes del servidor
hilo_escucha = threading.Thread(target=escuchar_servidor, args=(socket_cliente, clave_publica_servidor), daemon=True)
hilo_escucha.start()

# Bucle para enviar mensajes al servidor
while True:
    mensaje = input("Tú: ")
    # Firma el mensaje con la clave privada del cliente
    firma = clave_privada.sign(
        mensaje.encode('utf-8'),
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256()
    )
    # Envía el mensaje y la firma juntos, separados por '|||'
    socket_cliente.send(mensaje.encode('utf-8') + b'|||' + firma)