import socket
import threading

# Servidor mejorado: acepta múltiples clientes y hace broadcast de mensajes

clients = []
clients_lock = threading.Lock()

def escuchar_cliente(conexion, direccion):
    try:
        while True:
            data = conexion.recv(1024 * 1024)
            if not data:
                break
            try:
                mensaje = data.decode('utf-8')
            except Exception:
                mensaje = repr(data)
            print(f"Cliente {direccion}: {mensaje}")
            broadcast(mensaje, sender=conexion)
    except Exception:
        pass
    finally:
        with clients_lock:
            if conexion in clients:
                clients.remove(conexion)
        try:
            conexion.close()
        except Exception:
            pass
        print(f"Desconectado {direccion}")

def broadcast(mensaje, sender=None):
    with clients_lock:
        for c in list(clients):
            if c is sender:
                continue
            try:
                c.send(mensaje.encode('utf-8'))
            except Exception:
                # en caso de error, intentamos cerrar y remover
                try:
                    c.close()
                except Exception:
                    pass
                try:
                    clients.remove(c)
                except ValueError:
                    pass


def main():
    socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socket_servidor.bind(('0.0.0.0', 5000))
    socket_servidor.listen()
    print("Esperando conexiones en 0.0.0.0:5000...")

    try:
        while True:
            conexion, direccion = socket_servidor.accept()
            with clients_lock:
                clients.append(conexion)
            print(f"Nueva conexión desde {direccion}")
            hilo = threading.Thread(target=escuchar_cliente, args=(conexion, direccion), daemon=True)
            hilo.start()
            # servidor también puede enviar mensajes desde consola
            # si quieres enviar desde el servidor a todos, puedes usar broadcast desde aquí
    except KeyboardInterrupt:
        print('\nServidor detenido por teclado')
    finally:
        with clients_lock:
            for c in clients:
                try:
                    c.close()
                except Exception:
                    pass
        try:
            socket_servidor.close()
        except Exception:
            pass


if __name__ == '__main__':
    main()