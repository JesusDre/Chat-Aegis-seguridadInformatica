import socket          # Para comunicación entre computadoras
import threading       # Para ejecutar tareas en paralelo
from cryptography.hazmat.primitives import hashes      # Para funciones de hash
from cryptography.hazmat.primitives.asymmetric import rsa, padding  # Para claves y firmas
from cryptography.hazmat.primitives import serialization            # Para guardar/cargar claves

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
def verificar_firma(mensaje, firma, clave_publica_cliente):
    try:
        clave_publica_cliente.verify(
            firma,
            mensaje.encode('utf-8'),
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False


def escuchar_cliente(conexion, clave_publica_cliente):
    while True:
        datos = conexion.recv(4096)  # Recibe datos en bytes
        if not datos:
            break
        try:
            partes = datos.split(b'|||')
            mensaje = partes[0].decode('utf-8')
            firma = partes[1]
        except Exception:
            print("Formato de mensaje incorrecto.")
            continue

        # Verifica la firma con la clave pública del cliente
        if clave_publica_cliente and verificar_firma(mensaje, firma, clave_publica_cliente):
            print(f"\nCliente (verificado): {mensaje}")
        else:
            print("\n¡Advertencia! Mensaje no verificado.")

# --- CONFIGURACIÓN DEL SERVIDOR ---
socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_servidor.bind(('0.0.0.0', 5000))
socket_servidor.listen(1)
print("Esperando conexión...")

conexion, direccion = socket_servidor.accept()
print(f"Conectado con {direccion}")

# Envía la clave pública del servidor al cliente
conexion.send(clave_publica_pem)

# Recibe la clave pública del cliente
clave_publica_cliente_pem = conexion.recv(4096)
clave_publica_cliente = None
try:
    clave_publica_cliente = serialization.load_pem_public_key(clave_publica_cliente_pem)
except Exception:
    clave_publica_cliente = None

# Crea un hilo para escuchar los mensajes del cliente
hilo_escucha = threading.Thread(target=escuchar_cliente, args=(conexion, clave_publica_cliente), daemon=True)
hilo_escucha.start()

# Bucle para enviar mensajes al cliente
while True:
    mensaje = input("Tú: ")
    # Firma el mensaje con la clave privada del servidor
    firma = clave_privada.sign(
        mensaje.encode('utf-8'),
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256()
    )
    # Envía el mensaje y la firma juntos, separados por '|||'
    conexion.send(mensaje.encode('utf-8') + b'|||' + firma)