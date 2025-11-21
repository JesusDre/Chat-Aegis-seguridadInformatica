(function () {
  const chat = document.getElementById('chat');
  const hostInput = document.getElementById('host');
  const portInput = document.getElementById('wsport');
  const btnConnect = document.getElementById('btn-connect');
  const btnSend = document.getElementById('btn-send');
  const msgInput = document.getElementById('msg');
  const status = document.getElementById('ws-status');


  const signatureOverlay = document.getElementById('signature-overlay');
  const signatureDocName = document.getElementById('signature-doc-name');
  const signatureCancel = document.getElementById('signature-cancel');
  const signatureConfirm = document.getElementById('signature-confirm');


  // Elementos de archivo
  const fileInput = document.getElementById('upload');
  const btnPreview = document.getElementById('btn-preview');
  const btnSign = document.getElementById('btn-sign');

  let ws = null;
  let autoConnectAttempted = false;

  // Archivo recibido / listo para ver y confirmar
  let incomingFile = null; // { filename, mimeType, blob, previewUsed }

  function append(text, cls) {
    const el = document.createElement('div');
    el.className = 'message ' + (cls || '');
    el.textContent = text;
    chat.appendChild(el);
    chat.scrollTop = chat.scrollHeight;
  }

  function connect(host, port) {
    if (ws && ws.readyState === WebSocket.OPEN) return;
    const url = `ws://${host}:${port}/`;
    ws = new WebSocket(url);
    status.textContent = 'conectando';

    ws.addEventListener('open', () => {
      status.textContent = 'conectado';
      append('*** Conectado al proxy WebSocket ' + url + ' ***', 'meta');
    });

    ws.addEventListener('message', handleWsMessage);
    ws.addEventListener('close', () => {
      status.textContent = 'desconectado';
      append('*** Conexión cerrada ***', 'meta');
    });
    ws.addEventListener('error', () => {
      status.textContent = 'error';
      append('*** Error de WebSocket ***', 'meta');
    });
  }

  btnConnect.addEventListener('click', () => {
    const host = hostInput.value || 'localhost';
    const port = portInput.value || '8765';
    connect(host, port);
  });

  // =============================
  // ENVÍO DE MENSAJE + ARCHIVO
  // =============================

  function sendMessage() {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      append('*** No conectado. Haz click en Conectar primero ***', 'meta');
      return;
    }
    const text = msgInput.value.trim();
    const file = fileInput.files[0];

    if (!text && !file) return;

    // 1) mensaje de texto
    if (text) {
      ws.send(text);
      append('Tú: ' + text, 'me');
      msgInput.value = '';
    }

    // 2) archivo (si hay)
    if (file) {
      fileToBase64AndSend(file);
    }
  }

  btnSend.addEventListener('click', sendMessage);
  msgInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      sendMessage();
    }
  });

  window.addEventListener('load', () => {
    if (!autoConnectAttempted) {
      autoConnectAttempted = true;
      const host = hostInput.value || 'localhost';
      const port = portInput.value || '8765';
      setTimeout(() => connect(host, port), 500);
    }
  });

  fileInput.addEventListener('change', () => {
    const file = fileInput.files[0];
    if (file) append(`Archivo seleccionado: ${file.name}`, 'meta');
  });

  async function fileToBase64AndSend(file) {
    try {
      const buffer = await file.arrayBuffer();
      const bytes = new Uint8Array(buffer);
      let binary = '';
      for (let i = 0; i < bytes.length; i++) {
        binary += String.fromCharCode(bytes[i]);
      }
      const b64 = btoa(binary);
      const mime = file.type || 'application/pdf';

      // Enviar al otro lado
      ws.send(`FILE:${file.name}:${mime}:${b64}`);
      append(`Archivo "${file.name}" enviado al chat.`, 'meta');

      // 👉 También lo guardo localmente para poder verlo / confirmarlo aquí
      incomingFile = {
        filename: file.name,
        mimeType: mime,
        blob: new Blob([bytes], { type: mime }),
        previewUsed: false
      };
      btnPreview.disabled = false;
      btnSign.disabled = true;
      append('Puedes verlo una sola vez con el botón de abajo.', 'meta');

      fileInput.value = '';
    } catch (err) {
      console.error('Error leyendo archivo:', err);
      append('Error al enviar el archivo.', 'meta');
    }
  }

  // =============================
  // RECEPCIÓN DE MENSAJES
  // =============================

  function handleWsMessage(ev) {
    const data = ev.data;

    // 1) Archivo recibido desde el servidor: FILE:filename:mime:base64
    if (typeof data === 'string' && data.startsWith('FILE:')) {
      const parts = data.split(':');
      if (parts.length < 4) {
        append('*** Mensaje de archivo mal formado ***', 'meta');
        return;
      }
      const filename = parts[1];
      const mime = parts[2];
      const b64 = parts.slice(3).join(':');

      try {
        const byteChars = atob(b64);
        const byteNums = new Array(byteChars.length);
        for (let i = 0; i < byteChars.length; i++) {
          byteNums[i] = byteChars.charCodeAt(i);
        }
        const blob = new Blob([new Uint8Array(byteNums)], { type: mime });

        incomingFile = {
          filename,
          mimeType: mime,
          blob,
          previewUsed: false
        };

        append(`Te enviaron un archivo: ${filename}`, 'meta');
        append('Puedes verlo una sola vez y luego confirmarlo.', 'meta');
        btnPreview.disabled = false;
        btnSign.disabled = true;
      } catch (err) {
        console.error('Error decodificando archivo recibido:', err);
        append('Error al procesar el archivo recibido.', 'meta');
      }
      return;
    }

    // 2) Confirmación de firma (aquí vamos a mostrar el PDF firmado)
    if (typeof data === 'string' && data.startsWith('FIRMA_OK:')) {
      const parts = data.split(':');
      const filenameFirmado = parts[1] || (incomingFile && incomingFile.filename) || 'documento.pdf';

      append(`El archivo "${filenameFirmado}" fue firmado correctamente.`, 'meta');

      // Si tenemos el blob original, mostramos link como "PDF firmado"
      if (incomingFile && incomingFile.blob) {
        const url = URL.createObjectURL(incomingFile.blob);

        const wrapper = document.createElement('div');
        wrapper.className = 'message server';

        const title = document.createElement('div');
        title.textContent = `📄 Ver PDF firmado: ${filenameFirmado}`;
        title.style.fontWeight = 'bold';
        wrapper.appendChild(title);

        const link = document.createElement('a');
        link.href = url;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        link.textContent = 'Abrir PDF firmado';

        link.addEventListener('click', () => {
          // opcional: revocar después de abrir
          setTimeout(() => URL.revokeObjectURL(url), 2000);
        });

        wrapper.appendChild(link);
        chat.appendChild(wrapper);
        chat.scrollTop = chat.scrollHeight;
      }

      return;
    }

    // 3) Si es un chorro de base64 puro (ya NO es FILE ni FIRMA_OK), lo ocultamos
    if (
      typeof data === 'string' &&
      data.length > 80 &&
      /^[A-Za-z0-9+/=]+$/.test(data)
    ) {
      console.log('[DATOS BINARIOS RECIBIDOS OCULTOS]', data);
      append('*** Datos binarios recibidos (ocultos en la interfaz) ***', 'meta');
      return;
    }

    // 4) Mensajes normales
    append(data, 'server');
  }


  // =============================
  // VER ARCHIVO UNA SOLA VEZ (LINK)
  // =============================

  btnPreview.addEventListener('click', () => {
    if (!incomingFile || incomingFile.previewUsed) return;

    incomingFile.previewUsed = true;
    btnPreview.disabled = true;
    btnSign.disabled = false;

    const url = URL.createObjectURL(incomingFile.blob);

    const wrapper = document.createElement('div');
    wrapper.className = 'message server';

    const title = document.createElement('div');
    title.textContent = `📄 Enlace para ver ${incomingFile.filename} (solo una vez):`;
    title.style.fontWeight = 'bold';
    wrapper.appendChild(title);

    const link = document.createElement('a');
    link.href = url;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    link.textContent = 'Abrir documento';

    link.addEventListener('click', () => {
      link.textContent = 'Enlace usado';
      link.style.opacity = '0.5';
      link.style.pointerEvents = 'none';
      setTimeout(() => URL.revokeObjectURL(url), 2000);
    });

    wrapper.appendChild(link);
    chat.appendChild(wrapper);
    chat.scrollTop = chat.scrollHeight;
  });

  function abrirPanelFirma() {
    if (!incomingFile || !incomingFile.previewUsed) return;
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      append('*** No conectado. Haz click en Conectar primero ***', 'meta');
      return;
    }

    signatureDocName.textContent = incomingFile.filename || 'documento';
    signatureOverlay.style.display = 'flex';
  }

  function cerrarPanelFirma() {
    signatureOverlay.style.display = 'none';
  }

  // acción real de firmar (lo que antes estaba en btnSign)
  async function firmarDocumentoActual() {
    if (!incomingFile || !incomingFile.previewUsed) return;
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      append('*** No conectado. Haz click en Conectar primero ***', 'meta');
      return;
    }

    try {
      const buffer = await incomingFile.blob.arrayBuffer();
      const bytes = new Uint8Array(buffer);
      let binary = '';
      for (let i = 0; i < bytes.length; i++) binary += String.fromCharCode(bytes[i]);
      const b64 = btoa(binary);

      ws.send(`SIGNFILE:${incomingFile.filename}:${b64}`);
      append(`Enviando archivo "${incomingFile.filename}" para firma...`, 'meta');
      btnSign.disabled = true;
    } catch (err) {
      console.error('Error preparando archivo para firma:', err);
      append('Error al enviar el archivo para firma.', 'meta');
    } finally {
      cerrarPanelFirma();
    }
  }


  // =============================
  // CONFIRMAR / FIRMAR
  // =============================

  // Al pulsar el botón de abajo, solo abrimos el panel visual
  btnSign.addEventListener('click', () => {
    abrirPanelFirma();
  });

  // Botones dentro del panel
  signatureCancel.addEventListener('click', () => {
    cerrarPanelFirma();
  });

  signatureConfirm.addEventListener('click', () => {
    firmarDocumentoActual();
  });


})();
