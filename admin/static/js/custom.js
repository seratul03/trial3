async function ensure(){
  try{ await api('/me'); }catch(e){ location.href = '/'; }
}
ensure();

const form = document.getElementById('custom-form');
const tableBody = document.querySelector('#custom-table tbody');
let cached = [];

async function load(){
  cached = await api('/custom-replies');
  tableBody.innerHTML = '';
  if (!cached.length){
    tableBody.innerHTML = '<tr><td colspan="5">No custom replies yet</td></tr>';
    return;
  }
  cached.forEach(row=>{
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${row.id}</td>
      <td>${row.trigger}</td>
      <td>${row.priority}</td>
      <td><input type="checkbox" data-id="${row.id}" class="toggle" ${row.active ? 'checked' : ''}></td>
      <td><button data-id="${row.id}" class="delete">Delete</button></td>
    `;
    tableBody.appendChild(tr);
  });
  tableBody.querySelectorAll('.delete').forEach(btn=>btn.addEventListener('click', async ()=>{
    if (!confirm('Delete reply?')) return;
    await api('/custom-replies/'+btn.dataset.id,'DELETE');
    load();
  }));
  tableBody.querySelectorAll('.toggle').forEach(cb=>cb.addEventListener('change', async ()=>{
    const row = cached.find(r=>String(r.id)===String(cb.dataset.id));
    if (!row) return;
    await api('/custom-replies/'+row.id,'PUT', {
      trigger: row.trigger,
      response: row.response,
      priority: row.priority,
      active: cb.checked,
    });
    load();
  }));
}

form?.addEventListener('submit', async (e)=>{
  e.preventDefault();
  const trigger = form.elements['trigger'].value;
  const response = form.elements['response'].value;
  const priority = form.elements['priority'].value || 10;
  await api('/custom-replies','POST',{trigger,response,priority});
  form.reset();
  load();
});

load();
