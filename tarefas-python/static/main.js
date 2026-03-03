let tasks = [];
let visible = []; // flat visible ids
let selectedIndex = 0;

async function fetchTasks(){
  tasks = await (await fetch('/api/tasks')).json();
  buildAndRender();
}

function buildAndRender(){
  const byId = Object.fromEntries(tasks.map(t=>[t.id,t]));
  const children = {};
  tasks.forEach(t=>{ if(t.parent_id) { children[t.parent_id]=children[t.parent_id]||[]; children[t.parent_id].push(t.id); } });
  const roots = tasks.filter(t=>t.parent_id==null).map(t=>t.id);
  visible = [];
  const ul = document.createElement('ul');

  function walk(id, depth){
    const t = byId[id];
    const li = document.createElement('li');
    li.style.paddingLeft = (depth*16)+'px';
    const cnt = (children[id]||[]).length;
    const collapsed = !(t.expanded && t.expanded==1) && cnt>0;
    // show emoji if has details
    const hasDetails = t.details && String(t.details).trim().length>0;
    const emoji = hasDetails ? ' 📝' : '';
    // title plus child count (if collapsed)
    const titleTxt = collapsed ? `${escapeHtml(t.title)} [${cnt}]` : escapeHtml(t.title);
    const left = document.createElement('div'); left.className='left';
    left.innerHTML = titleTxt + emoji;
    const right = document.createElement('div'); right.className='right';
    // due date display
    if(t.due_date){
      const m = String(t.due_date).match(/^(\d{4})-(\d{2})-(\d{2})$/);
      if(m){
        const disp = `${m[3]}-${m[2]}-${m[1]}`;
        const days = daysUntil(m[1], m[2], m[3]);
        const color = days < 0 ? 'green' : (days < 4 ? 'red' : (days <= 7 ? 'yellow' : 'green'));
        right.innerHTML = `<span class="due-dot ${color}"></span><span class="due-text">${disp}</span>`;
      }
    }
    li.appendChild(left);
    li.appendChild(right);
    li.dataset.id = id;
    visible.push(id);
    ul.appendChild(li);
    if (t.expanded==1){
      (children[id]||[]).forEach(c=>walk(c, depth+1));
    }
  }
  roots.forEach(r=>walk(r,0));
  const container = document.getElementById('tree');
  container.innerHTML = '';
  container.appendChild(ul);
  clampSelection();
  highlight();
}

function daysUntil(yyyy, mm, dd){
  const target = new Date(Number(yyyy), Number(mm)-1, Number(dd));
  const today = new Date();
  // zero out time portion
  const t0 = Date.UTC(today.getFullYear(), today.getMonth(), today.getDate());
  const t1 = Date.UTC(target.getFullYear(), target.getMonth(), target.getDate());
  return Math.floor((t1 - t0) / (1000*60*60*24));
}

function escapeHtml(unsafe) {
  return String(unsafe)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function clampSelection(){
  if(visible.length===0){ selectedIndex = 0; return }
  if(selectedIndex < 0) selectedIndex = 0;
  if(selectedIndex >= visible.length) selectedIndex = visible.length-1;
}

function highlight(){
  document.querySelectorAll('li').forEach((li,i)=> {
    li.classList.toggle('selected', i===selectedIndex);
  });
}

async function command(cmd){
  const id = visible[selectedIndex];
  if(cmd==='o' && id){
    const t = tasks.find(x=>x.id==id);
    await fetch(`/api/tasks/${id}/toggle`, {method:'PATCH', headers:{'content-type':'application/json'}, body: JSON.stringify({expanded: !(t.expanded==1)})});
  }else if(cmd==='a'){ 
    // toggle all: if any is collapsed -> expand all, else collapse all
    const anyCollapsed = tasks.some(t=>{ const cnt = tasks.filter(x=>x.parent_id==t.id).length; return (t.expanded!=1) && cnt>0 });
    if(anyCollapsed) await fetch('/api/expand_all', {method:'POST'});
    else await fetch('/api/collapse_all', {method:'POST'});
  }
  else if(cmd==='h'){ await fetch('/api/collapse_all', {method:'POST'}); }
  else if(cmd==='p'){ const title=prompt('Título (nível principal)'); if(title) await fetch('/api/tasks',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({title})}); }
  else if(cmd==='s' && id){ const title=prompt('Título (sub)'); if(title) await fetch('/api/tasks',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({title,parent_id:id})}); }
  else if(cmd==='r' && id){ const title=prompt('Novo título'); if(title) await fetch(`/api/tasks/${id}/rename`,{method:'PATCH',headers:{'content-type':'application/json'},body:JSON.stringify({title})}); }
  else if(cmd==='x' && id){ if(confirm('Confirma?')) await fetch(`/api/tasks/${id}`,{method:'DELETE'}); }
  else if(cmd===',' && id){ // move up
    await fetch(`/api/tasks/${id}/move`, {method:'PATCH', headers:{'content-type':'application/json'}, body: JSON.stringify({dir:'up'})});
  }
  else if(cmd==='.' && id){ // move down
    await fetch(`/api/tasks/${id}/move`, {method:'PATCH', headers:{'content-type':'application/json'}, body: JSON.stringify({dir:'down'})});
  }
  else if(cmd==='d' && id){ // set due date
    await showDatePicker(id);
  }
  await fetchTasks();
}

// Editor overlay state
let editorOpen = false;

function openDetailsForSelected(){
  const id = visible[selectedIndex];
  if(!id) return;
  const t = tasks.find(x=>x.id==id);
  showEditor(id, t.details || '');
}

function showEditor(id, initialText){
  if(editorOpen) return;
  editorOpen = true;
  const overlay = document.createElement('div');
  overlay.className = 'editor-overlay';
  const panel = document.createElement('div'); panel.className='editor-panel';
  const left = document.createElement('div'); left.className='editor-left';
  const right = document.createElement('div'); right.className='editor-right';
  const ta = document.createElement('textarea'); ta.value = initialText;
  left.appendChild(ta);
  panel.appendChild(left);
  panel.appendChild(right);

  const toolbar = document.createElement('div'); toolbar.className='editor-toolbar editor-buttons';
  const btnSave = document.createElement('button'); btnSave.textContent='Salvar (Ctrl+S)';
  const btnCancel = document.createElement('button'); btnCancel.textContent='Cancelar (Esc)';
  toolbar.appendChild(btnCancel); toolbar.appendChild(btnSave);
  overlay.appendChild(panel);
  overlay.appendChild(toolbar);
  document.body.appendChild(overlay);

  function renderPreview(){
    const md = ta.value || '';
    right.innerHTML = marked.parse(md);
  }

  renderPreview();
  ta.focus();

  const onSave = async ()=>{
    await fetch(`/api/tasks/${id}/details`, {method:'PATCH', headers:{'content-type':'application/json'}, body: JSON.stringify({details: ta.value})});
    await fetchTasks();
    closeEditor();
  };
  const onCancel = ()=>{ closeEditor(); };

  btnSave.addEventListener('click', onSave);
  btnCancel.addEventListener('click', onCancel);
  ta.addEventListener('input', renderPreview);

  function keyHandler(e){
    if(e.key === 'Escape'){
      e.preventDefault();
      onCancel();
    }
    if((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 's'){
      e.preventDefault();
      onSave();
    }
  }

  document.addEventListener('keydown', keyHandler);

  function closeEditor(){
    document.removeEventListener('keydown', keyHandler);
    overlay.remove();
    editorOpen = false;
    // restore focus
    clampSelection();
    highlight();
  }
}

// simple date picker overlay
async function showDatePicker(id){
  if(editorOpen) return;
  editorOpen = true;
  const t = tasks.find(x=>x.id==id) || {};
  const overlay = document.createElement('div'); overlay.className='editor-overlay';
  const panel = document.createElement('div'); panel.className='editor-panel'; panel.style.maxWidth='420px'; panel.style.margin='auto'; panel.style.height='auto', panel.style.padding='12.5px';
  const inner = document.createElement('div'); inner.style.padding='12px'; inner.style.background='#fff'; inner.style.boxSizing='border-box';
  const label = document.createElement('div'); label.textContent = 'Selecionar data (ou deixar vazio para remover)'; label.style.marginBottom='8px';
  const input = document.createElement('input'); input.type='date'; input.style.fontSize='1rem';
  if(t.due_date){ input.value = t.due_date; }
  const btnSave = document.createElement('button'); btnSave.textContent='Salvar'; btnSave.style.marginLeft='8px';
  const btnCancel = document.createElement('button'); btnCancel.textContent='Cancelar'; btnCancel.style.marginLeft='8px';
  inner.appendChild(label); inner.appendChild(input); inner.appendChild(btnCancel); inner.appendChild(btnSave);
  panel.appendChild(inner); overlay.appendChild(panel); document.body.appendChild(overlay);

  function close(){ overlay.remove(); editorOpen=false; clampSelection(); highlight(); }
  btnCancel.addEventListener('click', ()=>{ close(); });
  btnSave.addEventListener('click', async ()=>{
    const v = input.value || null;
    await fetch(`/api/tasks/${id}/due_date`, {method:'PATCH', headers:{'content-type':'application/json'}, body: JSON.stringify({date: v})});
    close();
    await fetchTasks();
  });
}

document.addEventListener('keydown', async (e)=>{
  console.log('Keydown:', e.key);
  if(editorOpen) return; // let editor handle keys when open
  if(e.key === 'ArrowDown'){ selectedIndex++; clampSelection(); highlight(); e.preventDefault(); }
  else if(e.key === 'ArrowUp'){ selectedIndex--; clampSelection(); highlight(); e.preventDefault(); }
  else if(e.key === 'Enter'){ e.preventDefault(); openDetailsForSelected(); }
  else if(['p','s','r','x','o','a','h',',','.','d'].includes(e.key)){
    console.log("Epa!")
    e.preventDefault();
    await command(e.key);
  }
});

fetchTasks();
