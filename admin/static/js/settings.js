async function ensure(){
  try{ await api('/me'); }catch(e){ location.href = '/'; }
}
ensure();

document.getElementById('reseed-btn')?.addEventListener('click', async ()=>{
  if (!confirm('This will recreate the database and reseed mock data. Continue?')) return;
  try{
    const r = await api('/reseed','POST');
    if (r.ok) {
      alert('Database reseeded. Reloading...');
      location.href = '/';
    } else {
      alert('Reseed failed');
    }
  }catch(e){ alert('Reseed failed'); }
});
