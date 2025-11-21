"""
WebSocket <-> TCP proxy

- Serves a WebSocket server at ws://localhost:8765/
- For each browser connection, opens a TCP connection to the existing Python server
  (by default 127.0.0.1:5000) and forwards messages in both directions.
- Also helpful for local testing with the provided `servidor.py`.

Requires: websockets (install via `pip install -r requirements.txt`)

Run:
  python ws_proxy.py

Then open web/index.html in the browser (served by a simple HTTP server included automatically)
"""
import asyncio
import threading
import os
import http.server
import socketserver
import argparse

import websockets


DEFAULT_TCP_HOST = '127.0.0.1'
DEFAULT_TCP_PORT = 5000
WS_HOST = 'localhost'
WS_PORT = 8765
HTTP_PORT = 8000
WEB_DIR = os.path.join(os.path.dirname(__file__), 'web')


async def proxy_handler(websocket, path, tcp_host, tcp_port):
    """Handle a websocket client by opening a TCP connection to the chat server
    and relaying messages both ways.
    """
    print(f'WS client connected: {getattr(websocket, "remote_address", None)} path={path}')
    try:
        reader, writer = await asyncio.open_connection(tcp_host, tcp_port)
        print(f'  TCP connection established to {tcp_host}:{tcp_port} for WS client {getattr(websocket, "remote_address", None)}')
    except Exception as e:
        err_msg = f'*** Error conectando al servidor TCP: {e} ***'
        print(f'  {err_msg}')
        try:
            await websocket.send(err_msg)
        except Exception:
            pass
        try:
            await websocket.close()
        except Exception:
            pass
        return

    # Flag para saber si cerramos las tareas
    ws_to_tcp_task = None
    tcp_to_ws_task = None

    async def ws_to_tcp():
        try:
            async for msg in websocket:
                if isinstance(msg, str):
                    writer.write(msg.encode('utf-8'))
                    await writer.drain()
                else:
                    # binary
                    writer.write(msg)
                    await writer.drain()
        except websockets.ConnectionClosed:
            print(f'  WS closed for {getattr(websocket, "remote_address", None)}')
        except Exception as e:
            print(f'  Error en ws_to_tcp: {e}')
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    async def tcp_to_ws():
        try:
            while True:
                data = await reader.read(1024)
                if not data:
                    # connection closed
                    print(f'  TCP closed for {getattr(websocket, "remote_address", None)}')
                    try:
                        await websocket.send('*** Conexión cerrada por el servidor TCP ***')
                    except Exception:
                        pass
                    break
                try:
                    text = data.decode('utf-8')
                    await websocket.send(text)
                except Exception:
                    # fallback: send repr
                    try:
                        await websocket.send(repr(data))
                    except Exception:
                        pass
        except websockets.ConnectionClosed:
            print(f'  WS closed in tcp_to_ws for {getattr(websocket, "remote_address", None)}')
        except Exception as e:
            print(f'  Error en tcp_to_ws: {e}')
        finally:
            try:
                await websocket.close()
            except Exception:
                pass

    # run both tasks until one completes
    ws_to_tcp_task = asyncio.create_task(ws_to_tcp())
    tcp_to_ws_task = asyncio.create_task(tcp_to_ws())
    
    done, pending = await asyncio.wait(
        [ws_to_tcp_task, tcp_to_ws_task],
        return_when=asyncio.FIRST_COMPLETED,
    )
    for t in pending:
        t.cancel()
        try:
            await t
        except asyncio.CancelledError:
            pass
    print(f'WS client disconnected: {getattr(websocket, "remote_address", None)}')


def start_http_server(port=HTTP_PORT, web_dir=WEB_DIR):
    # Serve the `web` directory on HTTP_PORT in a background thread
    os.chdir(web_dir)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer((WS_HOST, port), handler) as httpd:
        print(f'HTTP server serving {web_dir} at http://{WS_HOST}:{port}/')
        httpd.serve_forever()


async def main(tcp_host, tcp_port, ws_host=WS_HOST, ws_port=WS_PORT):
    print(f'Starting WebSocket proxy on ws://{ws_host}:{ws_port}/ -> TCP {tcp_host}:{tcp_port}')
    async with websockets.serve(lambda ws, path: proxy_handler(ws, path, tcp_host, tcp_port), ws_host, ws_port):
        await asyncio.Future()  # run forever


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='WebSocket <-> TCP proxy for chat')
    parser.add_argument('--tcp-host', default=DEFAULT_TCP_HOST)
    parser.add_argument('--tcp-port', type=int, default=DEFAULT_TCP_PORT)
    parser.add_argument('--ws-host', default=WS_HOST)
    parser.add_argument('--ws-port', type=int, default=WS_PORT)
    parser.add_argument('--http-port', type=int, default=HTTP_PORT)
    args = parser.parse_args()

    # Start HTTP server in background thread
    http_thread = threading.Thread(target=start_http_server, args=(args.http_port, WEB_DIR), daemon=True)
    http_thread.start()

    try:
        asyncio.run(main(args.tcp_host, args.tcp_port, args.ws_host, args.ws_port))
    except KeyboardInterrupt:
        print('\nProxy detenido')
