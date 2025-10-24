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

Versiones

Version 1.0 - Chat básico sin cifrado
- cliente.py (MD5: 38fb9c39196476a4ce308e7c07816f4b89ccff60)
- servidor.py (MD5: eda81a3f5dcab34a6c3eb4ad7e4728b1d3402952)

Version 1.10 - Chat con cifrado simétrico y asimétrico
- servidorSimetrico.py (MD5: 26d8fb2f690c6ab5277c8005da368541616a0676)
- clienteSimetrico.py (MD5: 546a24a8b40a2a66c3bde4aa05682d0f021a5dc6)
- servidorAsimetrico.py (MD5: e841991154858ded0990be670d48e9509fc0cfb8)
- clienteAsimetrico.py (MD5: 9016697fa7720eadbd831a780e58cd5d30b98722)