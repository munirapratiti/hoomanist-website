// Step 2: GitHub sends the user back here with a code. Swap it for a token
// and hand that to the CMS window, which is listening for a postMessage.
module.exports = async (req, res) => {
  const { code, state } = req.query;

  const cookies = Object.fromEntries(
    (req.headers.cookie || '').split(';').map((c) => {
      const i = c.indexOf('=');
      return [c.slice(0, i).trim(), c.slice(i + 1)];
    }));

  if (!state || state !== cookies.oauth_state) {
    res.status(400).send('State tidak cocok. Ulangi login dari /admin.');
    return;
  }
  if (!code) {
    res.status(400).send('Tidak ada code dari GitHub.');
    return;
  }

  let token;
  try {
    const r = await fetch('https://github.com/login/oauth/access_token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({
        client_id: process.env.GITHUB_CLIENT_ID,
        client_secret: process.env.GITHUB_CLIENT_SECRET,
        code,
      }),
    });
    const data = await r.json();
    if (data.error || !data.access_token) {
      throw new Error(data.error_description || data.error || 'tanpa token');
    }
    token = data.access_token;
  } catch (err) {
    res.status(500).send('Gagal menukar code jadi token: ' + err.message);
    return;
  }

  // Clear the state cookie now that it has served its purpose.
  res.setHeader('Set-Cookie', 'oauth_state=; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=0');

  const payload = JSON.stringify({ token, provider: 'github' });
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.end(`<!DOCTYPE html><html><body><script>
(function () {
  function send() {
    // The CMS only accepts a message shaped exactly like this.
    window.opener.postMessage('authorization:github:success:${payload.replace(/'/g, "\\'")}', '*');
  }
  if (!window.opener) { document.body.textContent = 'Buka lagi dari /admin.'; return; }
  window.addEventListener('message', send, { once: true });
  window.opener.postMessage('authorizing:github', '*');
})();
</script>Berhasil masuk. Jendela ini akan menutup sendiri.</body></html>`);
};
