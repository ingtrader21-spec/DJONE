const $=s=>document.querySelector(s); let mode='assistant';
async function refresh(){try{let h=await fetch('/health').then(r=>r.json()),r=await fetch('/ready').then(r=>r.json());$('#health').textContent=h.status+' · '+h.environment;$('#status').textContent=JSON.stringify(r,null,2)}catch(e){$('#health').textContent='offline'}}
function log(x){$('#log').textContent=new Date().toLocaleTimeString()+'  '+x+'\n'+$('#log').textContent}
async function cmd(action,deck){let key=crypto.randomUUID();let r=await fetch('/v1/commands',{method:'POST',headers:{'Content-Type':'application/json','Idempotency-Key':key},body:JSON.stringify({action,deck})});let j=await r.json();log(action+' deck '+deck+' → '+(j.status||j.detail||r.status))}
function agent(){let p=$('#prompt').value.trim();if(!p)return;log('Agent request ('+mode+'): '+p);$('#prompt').value=''}
function emergency(){log('Emergency stop requested — UI control is display-only until authenticated server endpoint is implemented.')}
document.querySelectorAll('[data-mode]').forEach(b=>b.onclick=()=>{document.querySelectorAll('[data-mode]').forEach(x=>x.classList.remove('active'));b.classList.add('active');mode=b.dataset.mode;log('UI mode → '+mode)});
refresh();setInterval(refresh,5000);