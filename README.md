# Chat Aegis - Seguridad Informática

Sistema de chat en tiempo real con cifrado simétrico y asimétrico.

¿Qué es?
 Ambas partes usan la misma clave para cifrar y descifrar.

Cómo usar:
1. Abrir una terminal y ejecutar:
   python servidor_simetrico.py

2. Abrir otra terminal y ejecutar:
   python cliente_simetrico.py

3. Escribir mensajes y chatear

Características:
- Rápido y eficiente
- Ideal para comunicación donde ambos confían
- ⚠️ La clave debe compartirse de forma segura previamente

Cifrado Asimétrico

¿Qué es? 
Cada parte tiene un par de claves (pública y privada).
- La clave pública se comparte
- La clave privada es secreta

Características:
- Más seguro - no necesitas compartir claves secretas
- Las claves se generan automáticamente
- Cada uno mantiene su clave privada segura
- ⚠️ Un poco más lento que el simétrico

Diferencias Clave

| Característica | Simétrico -  | Asimétrico |
|----------------|--------------|------------|
| Velocidad      | ⚡ Rápido   | 🐢 Más lento |
| Seguridad      | 🔒 Buena    |  Excelente |
| Claves         | 1 compartida | 2 por usuario (pública/privada) |
| Intercambio de claves | Debe ser seguro | Automático y seguro |


¿Cómo Funciona?

Cifrado Simétrico:
Mensaje original → [Cifrar con CLAVE] 
→ 🔒 Mensaje cifrado 🔒 → [Descifrar con CLAVE] → Mensaje original

Cifrado Asimétrico:
Servidor envía:
Mensaje → [Cifrar con clave pública del Cliente] → 🔒 
→ [Cliente descifra con su clave privada] → Mensaje

Cliente envía:
Mensaje → [Cifrar con clave pública del Servidor] → 🔒
→ [Servidor descifra con su clave privada] → Mensaje

¿Qué es SHA256?
SHA-256 es una función de hash criptográfico que genera un “resumen” único de un mensaje.

Características:

- Garantiza integridad de los mensajes
- Permite autenticar al remitente
- ⚠️ No cifra el contenido, cualquiera podría leerlo
- 🔑 Requiere gestión de claves públicas y privadas

¿Cómo funciona?
Servidor envía:
Mensaje → [SHA-256 y firma con clave privada] → 🔏
→ [Cliente verifica firma con clave pública] → Mensaje verificado

Cliente envía:
Mensaje → [SHA-256 y firma con clave privada] → 🔏
→ [Servidor verifica firma con clave pública] → Mensaje verificado

Versiones

Version 1.0 - Chat básico sin cifrado
- cliente.py (MD5: 38fb9c39196476a4ce308e7c07816f4b89ccff60)
- servidor.py (MD5: eda81a3f5dcab34a6c3eb4ad7e4728b1d3402952)

Version 1.10 - Chat con cifrado simétrico y asimétrico
- servidorSimetrico.py (MD5: 26d8fb2f690c6ab5277c8005da368541616a0676)
- clienteSimetrico.py (MD5: 546a24a8b40a2a66c3bde4aa05682d0f021a5dc6)
- servidorAsimetrico.py (MD5:e841991154858ded0990be670d48e9509fc0cfb8)
- clienteAsimetrico.py (MD5: 9016697fa7720eadbd831a780e58cd5d30b98722)

Version 1.20 -Chat con SHA256
- clienteSha.py (MD5: 0185d1f222496ce1b1c2285514f225c0645d09a8)
- servidorSha.py (MD5: 40db39f103697cde1737b963932122fb990b2a72)

## Frontend (Interfaz gráfica)

Se agregó un cliente con interfaz gráfica usando Tkinter: `cliente_gui.py`.

Cómo usar el frontend:

1. Abrir una terminal y ejecutar el servidor (en la carpeta raíz del proyecto):

   ```powershell
   python .\servidor.py
   ```

2. En otra terminal (o desde el Explorador), ejecutar la GUI del cliente:

   ```powershell
   python .\cliente_gui.py
   ```

3. En la ventana del cliente, ingresar la dirección del servidor (por defecto 127.0.0.1) y el puerto (por defecto 5000), luego hacer clic en "Conectar". Escribir mensajes y presionar Enter o el botón "Enviar".

Notas:
- La GUI usa sockets TCP y el mismo protocolo simple que `cliente.py`/`servidor.py` (texto UTF-8). 
- Si quieres probar múltiples instancias de cliente, ejecuta varias copias de `cliente_gui.py`.
- Cerrar la ventana del cliente cerrará su socket y terminará la conexión limpiamente.

## Frontend web (HTML)

Hay una interfaz web que usa WebSockets. Como los navegadores no pueden abrir sockets TCP crudos,
se provee un pequeño proxy que traduce WebSocket <-> TCP para comunicar la página con `servidor.py`.

Archivo principal del proxy: `ws_proxy.py`.

Pasos para usar la interfaz web:

1. Instala dependencias (recomendado crear un entorno virtual):

   ```powershell
   python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
   ```

2. Ejecuta primero el servidor Python tradicional:

   ```powershell
   python .\servidor.py
   ```

3. En otra terminal ejecuta el proxy WebSocket (esto también inicia un servidor HTTP para los archivos estáticos):

   ```powershell
   python .\ws_proxy.py
   ```

   - El proxy por defecto intentará conectar al servidor TCP en 127.0.0.1:5000.
   - Servirá la página en http://localhost:8000/ y el endpoint WebSocket en ws://localhost:8765/.

4. Abre en Chrome la URL mostrada por el proxy (por defecto http://localhost:8000/) y usa la UI para conectar y chatear.

Notas:
- Si tu `servidor.py` usa otra IP/puerto, arranca `ws_proxy.py` con `--tcp-host` y `--tcp-port`.
- El proxy está pensado como una solución simple para testing/local; para producción usa HTTPS/WSS y autenticación.