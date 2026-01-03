async function ensure(){
  try{ await api('/me'); }catch(e){ location.href = '/'; }
}
ensure();

const form = document.getElementById('ctrl-form');
const statusEl = document.getElementById('ctrl-status');
const chatbotEnabledEl = document.getElementById('chatbot-enabled');
const maintenanceEl = document.getElementById('maintenance-mode');
const maintenanceReplyEl = document.getElementById('maintenance-reply');
const greetingEl = document.getElementById('greeting-message');
const fallbackEl = document.getElementById('fallback-message');
const toneEl = document.getElementById('tone');
const suggestionsEl = document.getElementById('suggestions-enabled');

function enforceMaintenanceToggle(){
  const isOn = chatbotEnabledEl.value === '1';
  maintenanceEl.disabled = !isOn;
  if (!isOn) maintenanceEl.value = '0';
}

async function loadControl(){
  const s = await api('/control');
  chatbotEnabledEl.value = s.chatbot_enabled || '1';
  maintenanceEl.value = s.maintenance_mode || '0';
  maintenanceReplyEl.value = s.maintenance_reply || '';
  greetingEl.value = s.greeting_message || '';
  fallbackEl.value = s.fallback_message || '';
  toneEl.value = s.tone || 'neutral';
  suggestionsEl.value = s.suggestions_enabled || '1';
  enforceMaintenanceToggle();
}

chatbotEnabledEl?.addEventListener('change', enforceMaintenanceToggle);

form?.addEventListener('submit', async (e)=>{
  e.preventDefault();
  const payload = {
    chatbot_enabled: chatbotEnabledEl.value,
    maintenance_mode: maintenanceEl.value,
    maintenance_reply: maintenanceReplyEl.value,
    greeting_message: greetingEl.value,
    fallback_message: fallbackEl.value,
    tone: toneEl.value,
    suggestions_enabled: suggestionsEl.value,
  };
  const res = await api('/control','POST', payload);
  statusEl.textContent = 'Saved. Maintenance mode is ' + (res.maintenance_mode === '1' ? 'ON' : 'OFF') + ' | Chatbot ' + (res.chatbot_enabled === '1' ? 'ON' : 'OFF');
  enforceMaintenanceToggle();
});

loadControl();
