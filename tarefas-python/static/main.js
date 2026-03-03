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
    li.textContent = collapsed ? `${t.title} [${cnt}]` : t.title;
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
  }else if(cmd==='a'){ await fetch('/api/expand_all', {method:'POST'}); }
  else if(cmd==='h'){ await fetch('/api/collapse_all', {method:'POST'}); }
  else if(cmd==='p'){ const title=prompt('Título (nível principal)'); if(title) await fetch('/api/tasks',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({title})}); }
  else if(cmd==='s' && id){ const title=prompt('Título (sub)'); if(title) await fetch('/api/tasks',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({title,parent_id:id})}); }
  else if(cmd==='r' && id){ const title=prompt('Novo título'); if(title) await fetch(`/api/tasks/${id}/rename`,{method:'PATCH',headers:{'content-type':'application/json'},body:JSON.stringify({title})}); }
  else if(cmd==='x' && id){ if(confirm('Confirma?')) await fetch(`/api/tasks/${id}`,{method:'DELETE'}); }
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

document.addEventListener('keydown', async (e)=>{
  if(editorOpen) return; // let editor handle keys when open
  if(e.key === 'ArrowDown'){ selectedIndex++; clampSelection(); highlight(); e.preventDefault(); }
  else if(e.key === 'ArrowUp'){ selectedIndex--; clampSelection(); highlight(); e.preventDefault(); }
  else if(e.key === 'Enter'){ e.preventDefault(); openDetailsForSelected(); }
  else if(['p','s','r','x','o','a','h','q'].includes(e.key)){
    e.preventDefault();
    if(e.key==='q'){ /* can navigate away or close */ }
    else await command(e.key);
  }
});

fetchTasks();
