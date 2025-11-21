import socket
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText


class ChatClientGUI:
    def __init__(self, master):
        self.master = master
        master.title('Cliente Chat - GUI')

        # --- Variables ---
        self.sock = None
        self.listener_thread = None
        self.connected = False

        # --- Frame de conexión ---
        frm_conn = ttk.Frame(master, padding=8)
        frm_conn.grid(row=0, column=0, sticky='ew')

        ttk.Label(frm_conn, text='Servidor:').grid(row=0, column=0, sticky='w')
        self.entry_host = ttk.Entry(frm_conn, width=18)
        self.entry_host.insert(0, '127.0.0.1')
        self.entry_host.grid(row=0, column=1, padx=(4, 12))

        ttk.Label(frm_conn, text='Puerto:').grid(row=0, column=2, sticky='w')
        self.entry_port = ttk.Entry(frm_conn, width=6)
        self.entry_port.insert(0, '5000')
        self.entry_port.grid(row=0, column=3, padx=(4, 12))

        self.btn_connect = ttk.Button(frm_conn, text='Conectar', command=self.connect_to_server)
        self.btn_connect.grid(row=0, column=4)

        # --- Area de chat ---
        frm_chat = ttk.Frame(master, padding=(8, 0, 8, 8))
        frm_chat.grid(row=1, column=0, sticky='nsew')
        master.rowconfigure(1, weight=1)
        master.columnconfigure(0, weight=1)

        self.txt_chat = ScrolledText(frm_chat, state='disabled', wrap='word', height=18)
        self.txt_chat.grid(row=0, column=0, sticky='nsew')
        frm_chat.rowconfigure(0, weight=1)
        frm_chat.columnconfigure(0, weight=1)

        # --- Entrada y enviar ---
        frm_send = ttk.Frame(master, padding=8)
        frm_send.grid(row=2, column=0, sticky='ew')

        self.entry_msg = ttk.Entry(frm_send)
        self.entry_msg.grid(row=0, column=0, sticky='ew', padx=(0, 8))
        frm_send.columnconfigure(0, weight=1)
        self.entry_msg.bind('<Return>', lambda e: self.send_message())

        self.btn_send = ttk.Button(frm_send, text='Enviar', command=self.send_message, state='disabled')
        self.btn_send.grid(row=0, column=1)

        # Cerrar correctamente
        master.protocol('WM_DELETE_WINDOW', self.on_close)

    def append_message(self, msg):
        # Thread-safe append usando after
        def _append():
            self.txt_chat['state'] = 'normal'
            self.txt_chat.insert('end', msg + '\n')
            self.txt_chat.see('end')
            self.txt_chat['state'] = 'disabled'
        self.master.after(0, _append)

    def connect_to_server(self):
        if self.connected:
            return
        host = self.entry_host.get().strip()
        try:
            port = int(self.entry_port.get().strip())
        except ValueError:
            messagebox.showerror('Puerto inválido', 'El puerto debe ser un número entero')
            return

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, port))
        except Exception as e:
            messagebox.showerror('Error de conexión', f'No se pudo conectar: {e}')
            self.sock = None
            return

        self.connected = True
        self.btn_connect['state'] = 'disabled'
        self.entry_host['state'] = 'disabled'
        self.entry_port['state'] = 'disabled'
        self.btn_send['state'] = 'enabled'
        self.append_message(f'Conectado a {host}:{port}')

        # Iniciar hilo de escucha
        self.listener_thread = threading.Thread(target=self.listen_server, daemon=True)
        self.listener_thread.start()

    def listen_server(self):
        try:
            while True:
                data = self.sock.recv(1024)
                if not data:
                    # Se desconectó
                    self.append_message('*** Conexión cerrada por el servidor ***')
                    break
                try:
                    text = data.decode('utf-8')
                except Exception:
                    text = repr(data)
                self.append_message(f'Servidor: {text}')
        except Exception as e:
            self.append_message(f'*** Error en recepción: {e} ***')
        finally:
            self.connected = False
            # Habilitar reconexión en UI
            def _update():
                self.btn_connect['state'] = 'normal'
                self.entry_host['state'] = 'normal'
                self.entry_port['state'] = 'normal'
                self.btn_send['state'] = 'disabled'
            self.master.after(0, _update)

    def send_message(self):
        if not self.connected or not self.sock:
            messagebox.showwarning('No conectado', 'Conéctate al servidor primero')
            return
        msg = self.entry_msg.get().strip()
        if not msg:
            return
        try:
            self.sock.send(msg.encode('utf-8'))
            self.append_message(f'Tú: {msg}')
            self.entry_msg.delete(0, 'end')
        except Exception as e:
            messagebox.showerror('Error al enviar', f'No se pudo enviar el mensaje: {e}')

    def on_close(self):
        try:
            if self.sock:
                try:
                    self.sock.shutdown(socket.SHUT_RDWR)
                except Exception:
                    pass
                self.sock.close()
        except Exception:
            pass
        self.master.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('600x420')
    app = ChatClientGUI(root)
    root.mainloop()
