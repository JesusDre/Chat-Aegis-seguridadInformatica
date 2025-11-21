(function(){
  const chat = document.getElementById('chat');
  const hostInput = document.getElementById('host');
  const portInput = document.getElementById('wsport');
  const btnConnect = document.getElementById('btn-connect');
  const btnSend = document.getElementById('btn-send');
  const msgInput = document.getElementById('msg');
  const status = document.getElementById('ws-status');

  let ws = null;
  let autoConnectAttempted = false;

  function append(text, cls){
    const el = document.createElement('div');
    el.className = 'message ' + (cls||'');
    el.textContent = text;
    chat.appendChild(el);
    chat.scrollTop = chat.scrollHeight;
  }

  function connect(host, port) {
    if(ws && ws.readyState === WebSocket.OPEN) return;
    const url = `ws://${host}:${port}/`;
    ws = new WebSocket(url);
    status.textContent = 'conectando';

    ws.addEventListener('open', ()=>{
      status.textContent = 'conectado';
      append('*** Conectado al proxy WebSocket ' + url + ' ***', 'meta');
    });

    ws.addEventListener('message', (ev)=>{
      append(ev.data, 'server');
    });

    ws.addEventListener('close', ()=>{
      status.textContent = 'desconectado';
      append('*** Conexión cerrada ***', 'meta');
    });

    ws.addEventListener('error', (e)=>{
      status.textContent = 'error';
      append('*** Error de WebSocket ***', 'meta');
    });
  }

  btnConnect.addEventListener('click', ()=>{
    const host = hostInput.value || 'localhost';
    const port = portInput.value || '8765';
    connect(host, port);
  });

  function sendMessage(){
    if(!ws || ws.readyState !== WebSocket.OPEN){
      append('*** No conectado. Haz click en Conectar primero ***', 'meta');
      return;
    }
    const text = msgInput.value.trim();
    if(!text) return;
    ws.send(text);
    append('Tú: ' + text, 'me');
    msgInput.value = '';
    msgInput.focus();
  }

  btnSend.addEventListener('click', sendMessage);
  msgInput.addEventListener('keydown', (e)=>{ if(e.key === 'Enter') sendMessage(); });

  // Auto-conectar al cargar la página
  window.addEventListener('load', ()=>{
    if(!autoConnectAttempted) {
      autoConnectAttempted = true;
      const host = hostInput.value || 'localhost';
      const port = portInput.value || '8765';
      setTimeout(() => connect(host, port), 500);
    }
  });

})();
