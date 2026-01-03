async function api(path, method='GET', body) {
  const opts = {method, headers: {'Content-Type':'application/json'}};
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch('/api' + path, opts);
  if (res.status === 401) {
    window.location = '/';
    throw new Error('unauthorized');
  }
  return res.json();
}

async function rawFetch(path, method='GET', body){
  const opts = {method, headers:{'Content-Type':'application/json'}};
  if (body) opts.body = JSON.stringify(body);
  return fetch('/api'+path, opts);
}
