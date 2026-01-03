async function ensure(){
  try{ await api('/me'); }catch(e){ location.href = '/'; }
}
ensure();

async function loadKB(){
  const items = await api('/kb');
  const tbody = document.querySelector('#kb-table tbody');
  tbody.innerHTML='';
  items.forEach(item=>{
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${item.id}</td><td>${item.title}</td><td>${item.department}</td><td>${item.active? 'Yes':'No'}</td><td><button class="delete">Delete</button></td>`;
    tbody.appendChild(tr);
  });
  document.querySelectorAll('.delete').forEach((b, idx)=>{
    b.addEventListener('click', async ()=>{
      if (!confirm('Delete KB item?')) return;
      const id = items[idx].id;
      await api('/kb/'+id,'DELETE');
      loadKB();
    });
  });
}

document.getElementById('create-kb-form')?.addEventListener('submit', async (e)=>{
  e.preventDefault();
  const title = document.getElementById('kb-title').value;
  const dept = document.getElementById('kb-dept').value;
  const tags = document.getElementById('kb-tags').value;
  const content = document.getElementById('kb-content').value;
  const active = document.getElementById('kb-active').checked;
  await api('/kb','POST',{title,content,department:dept,tags,active});
  document.getElementById('kb-title').value='';
  document.getElementById('kb-content').value='';
  loadKB();
});

loadKB();
