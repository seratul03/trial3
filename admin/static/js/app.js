async function api(path, method='GET', body) {
  const opts = {method, headers: {'Content-Type':'application/json'}};
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch('/api' + path, opts);
  if (res.status === 401) throw new Error('unauthorized');
  return res.json();
}

// Login
const loginForm = document.getElementById('login-form');
const loginMsg = document.getElementById('login-msg');
const loginBox = document.getElementById('login-box');
const dashboard = document.getElementById('dashboard');
const adminEmailSpan = document.getElementById('admin-email');

loginForm?.addEventListener('submit', async (e)=>{
  e.preventDefault();
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  try{
    const r = await api('/login','POST',{email,password});
    if (r.ok) loadDashboard();
  }catch(err){ loginMsg.textContent = 'Login failed'; }
});

document.getElementById('logout-btn')?.addEventListener('click', async ()=>{
  await api('/logout','POST');
  sessionOut();
});

function sessionOut(){
  dashboard.style.display='none';
  loginBox.style.display='block';
}

async function loadDashboard(){
  try{
    const me = await api('/me');
    if (!me.admin) return;
    adminEmailSpan.textContent = me.admin.email;
    loginBox.style.display='none';
    dashboard.style.display='block';
    showTab('users');
    loadUsers();
    loadKB();
    loadSessions();
    loadAnalytics();
  }catch(err){ sessionOut(); }
}

// Tabs
document.querySelectorAll('.tabs button').forEach(b=>b.addEventListener('click', ()=>{
  document.querySelectorAll('.tabs button').forEach(x=>x.classList.remove('active'));
  b.classList.add('active');
  showTab(b.dataset.tab);
}));
function showTab(name){
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  const el = document.getElementById('tab-'+name);
  if (el) el.classList.add('active');
}

// Users
async function loadUsers(){
  const users = await api('/users');
  const tbody = document.querySelector('#users-table tbody');
  tbody.innerHTML = '';
  users.forEach(u=>{
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${u.email}</td><td><select class="role-select"><option value="admin">admin</option><option value="moderator">moderator</option><option value="superadmin">superadmin</option></select></td><td>${u.created_at||''}</td><td><button class="delete-user">Delete</button></td>`;
    tbody.appendChild(tr);
  });
  // set selects and delete buttons
  document.querySelectorAll('#users-table tbody tr').forEach((tr, idx)=>{
    const sel = tr.querySelector('.role-select');
    sel.value = users[idx].role;
    sel.addEventListener('change', async ()=>{
      const email = users[idx].email;
      const role = sel.value;
      await api('/users/'+encodeURIComponent(email),'PUT',{role});
      loadUsers();
    });
    tr.querySelector('.delete-user').addEventListener('click', async ()=>{
      if (!confirm('Delete user '+users[idx].email+'?')) return;
      await api('/users/'+encodeURIComponent(users[idx].email),'DELETE');
      loadUsers();
    });
  });
}

document.getElementById('create-user-form')?.addEventListener('submit', async (e)=>{
  e.preventDefault();
  const email = document.getElementById('new-user-email').value;
  const password = document.getElementById('new-user-password').value;
  const role = document.getElementById('new-user-role').value;
  try{
    await api('/users','POST',{email,password,role});
    document.getElementById('new-user-email').value='';
    document.getElementById('new-user-password').value='';
    loadUsers();
  }catch(err){ alert('Error creating user'); }
});

// KB
async function loadKB(){
  const items = await api('/kb');
  const tbody = document.querySelector('#kb-table tbody');
  tbody.innerHTML='';
  items.forEach(item=>{
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${item.id}</td><td>${item.title}</td><td>${item.department}</td><td>${item.active? 'Yes':'No'}</td><td><button data-id="${item.id}" class="kb-delete">Delete</button></td>`;
    tbody.appendChild(tr);
  });
  document.querySelectorAll('.kb-delete').forEach(b=>b.addEventListener('click', async ()=>{
    const id = b.dataset.id;
    if (!confirm('Delete KB item '+id+'?')) return;
    await api('/kb/'+id,'DELETE');
    loadKB();
  }));
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

// Sessions
async function loadSessions(){
  const sessions = await api('/sessions');
  const tbody = document.querySelector('#sessions-table tbody');
  tbody.innerHTML='';
  sessions.forEach(s=>{
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${s.id}</td><td>${s.user_email}</td><td>${s.transcript}</td><td>${s.status}</td><td>${s.started_at||''}</td><td><button class="view-session">View</button></td>`;
    tbody.appendChild(tr);
  });
  document.querySelectorAll('.view-session').forEach((b, idx)=>{
    b.addEventListener('click', async ()=>{
      const id = sessions[idx].id;
      const data = await api('/sessions/'+id);
      alert(JSON.stringify(data, null, 2));
    });
  });
}

document.getElementById('simulate-session-form')?.addEventListener('submit', async (e)=>{
  e.preventDefault();
  const email = document.getElementById('sim-email').value;
  const text = document.getElementById('sim-text').value;
  const status = document.getElementById('sim-status').value;
  await api('/simulate-session','POST',{user_email:email,transcript:text,status});
  document.getElementById('sim-email').value='';
  document.getElementById('sim-text').value='';
  loadSessions();
  loadAnalytics();
});

// Analytics
async function loadAnalytics(){
  const a = await api('/analytics');
  document.getElementById('stat-sessions').textContent = a.total_sessions;
  document.getElementById('stat-unanswered').textContent = a.unanswered_sessions;
  document.getElementById('stat-kb').textContent = a.total_kb;
}

document.getElementById('export-sessions')?.addEventListener('click', async ()=>{
  try{
    const res = await fetch('/api/export/sessions');
    if (!res.ok) throw new Error('export failed');
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = 'sessions.csv'; document.body.appendChild(a); a.click(); a.remove();
  }catch(e){ alert('Export failed'); }
});

// Audit
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

// Settings - reseed
document.getElementById('reseed-btn')?.addEventListener('click', async ()=>{
  if (!confirm('This will recreate the database and reseed mock data. Continue?')) return;
  try{
    const r = await api('/reseed','POST');
    if (r.ok) {
      alert('Database reseeded. Reloading...');
      location.reload();
    } else {
      alert('Reseed failed');
    }
  }catch(e){ alert('Reseed failed'); }
});

// On load, check if logged in
window.addEventListener('load', async ()=>{
  try{ await loadDashboard(); }catch(e){}
});
