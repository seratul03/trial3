async function ensure(){
  try{ await api('/me'); }catch(e){ location.href = '/'; }
}
ensure();

async function loadAudit(){
  const audits = await api('/audit');
  const tbody = document.querySelector('#audit-table tbody');
  tbody.innerHTML='';
  audits.forEach(a=>{
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${a.id}</td><td>${a.admin_email||''}</td><td>${a.action}</td><td>${a.detail}</td><td>${a.ts}</td>`;
    tbody.appendChild(tr);
  });
  const feedback = await api('/feedback');
  const ft = document.querySelector('#feedback-table tbody');
  ft.innerHTML='';
  feedback.forEach(f=>{
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${f.id}</td><td>${f.user_email}</td><td>${f.message}</td><td>${f.created_at}</td>`;
    ft.appendChild(tr);
  });
}

document.getElementById('refresh-audit')?.addEventListener('click', loadAudit);
loadAudit();
