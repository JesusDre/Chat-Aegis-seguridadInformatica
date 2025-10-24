import socket          # Importa la librería para comunicación entre computadoras
import threading       # Importa la librería para ejecutar tareas en paralelo

# Función que escucha los mensajes del servidor (sin verificación HMAC)
def escuchar_servidor(socket_cliente):
    while True:
        datos = socket_cliente.recv(2048).decode('utf-8')
        if not datos:
            break
        print(f"\nServidor: {datos}")

# --- CONFIGURACIÓN DEL CLIENTE ---
def main():
    socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_cliente.connect(('127.0.0.1', 5000))
    print("Conectado al servidor.")

    # Creamos un hilo para escuchar mensajes del servidor sin bloquear el hilo principal
    hilo_escucha = threading.Thread(target=escuchar_servidor, args=(socket_cliente,), daemon=True)
    hilo_escucha.start()

    # Bucle principal para enviar mensajes al servidor.
    try:
        while True:
            mensaje = input("Tú: ")
            socket_cliente.send(mensaje.encode('utf-8'))
    except (KeyboardInterrupt, EOFError):
        print('\nSaliendo...')
        socket_cliente.close()

if __name__ == '__main__':
    main()