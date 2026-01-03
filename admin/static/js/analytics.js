async function ensure(){
  try{ await api('/me'); }catch(e){ location.href = '/'; }
}
ensure();

async function loadAnalytics(){
  const a = await api('/analytics');
  document.getElementById('stat-sessions').textContent = a.total_sessions;
  document.getElementById('stat-unanswered').textContent = a.unanswered_sessions;
  document.getElementById('stat-kb').textContent = a.total_kb;
}

async function loadDailyUsers(){
  const table = document.querySelector('#daily-users-table tbody');
  const rows = await api('/analytics/daily-users');
  const entries = Object.entries(rows);
  if (!entries.length){
    table.innerHTML = '<tr><td colspan="2">No data</td></tr>';
    return;
  }
  table.innerHTML = '';
  const sorted = entries.sort((a,b)=> a[0] < b[0] ? 1 : -1);
  const latest = sorted[0];
  if (latest){
    document.getElementById('stat-users-today').textContent = latest[1];
  }
  sorted.forEach(([day, count])=>{
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${day}</td><td>${count}</td>`;
    table.appendChild(tr);
  });
}

async function loadCategories(){
  const table = document.querySelector('#categories-table tbody');
  let rows = await api('/categories');
  let entries = Object.entries(rows || {});
  if (!entries.length){
    await api('/classify','POST');
    rows = await api('/categories');
    entries = Object.entries(rows || {});
  }
  if (!entries.length){ table.innerHTML = '<tr><td colspan="2">No categories yet</td></tr>'; return; }
  table.innerHTML = '';
  entries.sort((a,b)=> b[1]-a[1]).forEach(([cat, count])=>{
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${cat}</td><td>${count}</td>`;
    table.appendChild(tr);
  });
}

document.getElementById('export-sessions')?.addEventListener('click', async ()=>{
  try{
    const res = await rawFetch('/export/sessions');
    if (!res.ok) throw new Error('export failed');
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = 'sessions.csv'; document.body.appendChild(a); a.click(); a.remove();
  }catch(e){ alert('Export failed'); }
});

document.getElementById('reclassify')?.addEventListener('click', async ()=>{
  await api('/classify','POST');
  await loadCategories();
});

loadAnalytics();
loadDailyUsers();
loadCategories();
