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

document.addEventListener('keydown', async (e)=>{
  if(e.key === 'ArrowDown'){ selectedIndex++; clampSelection(); highlight(); e.preventDefault(); }
  else if(e.key === 'ArrowUp'){ selectedIndex--; clampSelection(); highlight(); e.preventDefault(); }
  else if(e.key === 'Enter'){ /* could open detail or noop */ }
  else if(['p','s','r','x','o','a','h','q'].includes(e.key)){
    e.preventDefault();
    if(e.key==='q'){ /* can navigate away or close */ }
    else await command(e.key);
  }
});

fetchTasks();
