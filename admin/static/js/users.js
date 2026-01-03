async function ensure(){
  try{ await api('/me'); }catch(e){ location.href = '/'; }
}
ensure();

async function loadUsers(){
  const users = await api('/users');
  const tbody = document.querySelector('#users-table tbody');
  tbody.innerHTML = '';
  users.forEach(u=>{
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${u.email}</td><td>${u.created_at||''}</td><td><button class="delete">Delete</button></td>`;
    tbody.appendChild(tr);
  });
  document.querySelectorAll('.delete').forEach((b, idx)=>{
    b.addEventListener('click', async ()=>{
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
  await api('/users','POST',{email,password});
  document.getElementById('new-user-email').value='';
  document.getElementById('new-user-password').value='';
  loadUsers();
});

loadUsers();
