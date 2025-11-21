# servidor_firma.py

import socket
import threading
import base64
from firma import generar_llaves, firmar_bytes

HOST = "0.0.0.0"
PORT = 6000   # Otro puerto interno para firma digital

generar_llaves()
print(f"Servidor de firma digital escuchando en {HOST}:{PORT}")

def manejar_cliente(conn, addr):
    print("Cliente conectado:", addr)
    try:
        while True:
            data = conn.recv(4096).decode()
            if not data:
                break

            if data.startswith("FIRMAR:"):
                nombre, b64data = data.split(":", 2)[1:]
                archivo = base64.b64decode(b64data)

                firma = firmar_bytes(archivo)

                respuesta = f"FIRMA_OK:{nombre}:{firma}"
                conn.sendall(respuesta.encode())
    except:
        pass

    conn.close()
    print("Cliente desconectado:", addr)


def iniciar():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    while True:
        conn, addr = server.accept()
        hilo = threading.Thread(target=manejar_cliente, args=(conn, addr))
        hilo.start()


if __name__ == "__main__":
    iniciar()
