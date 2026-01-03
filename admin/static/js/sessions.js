async function ensure(){
  try{ await api('/me'); }catch(e){ location.href = '/'; }
}
ensure();

async function loadSessions(){
  const sessions = await api('/sessions');
  const tbody = document.querySelector('#sessions-table tbody');
  tbody.innerHTML='';
  sessions.forEach(s=>{
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${s.id}</td><td>${s.user_email}</td><td>${s.transcript}</td><td>${s.status}</td><td>${s.started_at||''}</td><td><button class="view">View</button></td>`;
    tbody.appendChild(tr);
  });
  document.querySelectorAll('.view').forEach((b, idx)=>{
    b.addEventListener('click', async ()=>{
      const id = sessions[idx].id;
      const data = await api('/sessions/'+id);
      alert(JSON.stringify(data, null, 2));
    });
  });
}

async function loadUnanswered(){
  const container = document.getElementById('unanswered-list');
  const items = await api('/unanswered');
  if (!items.length){
    container.innerHTML = '<div class="muted">No unanswered questions.</div>';
    return;
  }
  container.innerHTML = '';
  items.forEach(item=>{
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `
      <div><strong>#${item.id}</strong> ${item.user_email||''}</div>
      <div class="muted" style="margin:4px 0">${item.transcript||''}</div>
      <textarea rows="2" class="answer" placeholder="Type your answer..."></textarea>
      <label><input type="checkbox" class="add-kb" checked> Add to KB</label>
      <label><input type="checkbox" class="add-custom"> Save as custom reply</label>
      <button class="submit-answer">Submit Answer</button>
    `;
    container.appendChild(card);
    const answerEl = card.querySelector('.answer');
    const addKbEl = card.querySelector('.add-kb');
    const addCustomEl = card.querySelector('.add-custom');
    card.querySelector('.submit-answer').addEventListener('click', async ()=>{
      const answer = answerEl.value.trim();
      if (!answer) { alert('Answer is required'); return; }
      await api(`/unanswered/${item.id}/answer`, 'POST', {
        answer,
        add_to_kb: addKbEl.checked,
        save_as_custom_reply: addCustomEl.checked,
      });
      loadUnanswered();
      loadSessions();
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
  loadUnanswered();
});

loadSessions();
loadUnanswered();
