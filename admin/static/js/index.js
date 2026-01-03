const loginForm = document.getElementById('login-form');
const msg = document.getElementById('msg');
loginForm.addEventListener('submit', async (e)=>{
  e.preventDefault();
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  try{
    const r = await api('/login','POST',{email,password});
    if (r.ok) {
      // redirect to users page by default
      location.href = '/static/users.html';
    }
  }catch(err){ msg.textContent = 'Login failed'; }
});
