// Step 1 of the GitHub sign-in for /admin: hand the browser to GitHub.
//
// The client secret must never reach the browser, so the code-for-token swap
// happens in callback.js on the server. This endpoint only starts the dance.
const crypto = require('crypto');

module.exports = (req, res) => {
  const clientId = process.env.GITHUB_CLIENT_ID;
  if (!clientId) {
    res.status(500).send('GITHUB_CLIENT_ID belum diset di Vercel.');
    return;
  }

  // Random state, echoed back by GitHub, so a forged callback can be rejected.
  const state = crypto.randomBytes(16).toString('hex');
  res.setHeader('Set-Cookie',
    `oauth_state=${state}; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=600`);

  const url = new URL('https://github.com/login/oauth/authorize');
  url.searchParams.set('client_id', clientId);
  url.searchParams.set('scope', 'repo,user');
  url.searchParams.set('state', state);

  res.writeHead(302, { Location: url.toString() });
  res.end();
};
