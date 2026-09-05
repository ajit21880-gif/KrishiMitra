const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const path = require('path');
const fs = require('fs');
const { exec } = require('child_process');
const axios = require('axios');

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

console.log('====================================================');
console.log('   KrishiMitra WhatsApp Web Gateway Starting...    ');
console.log('====================================================');
console.log(`Target Backend API: ${BACKEND_URL}`);

const client = new Client({
  authStrategy: new LocalAuth({
    dataPath: path.resolve('./.wwebjs_auth')
  }),
  puppeteer: {
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  }
});

client.on('qr', (qr) => {
  console.log('\n[QR CODE] Scan the QR code below using WhatsApp on your phone:');
  qrcode.generate(qr, { small: true });

  try {
    const htmlContent = `<!DOCTYPE html>
<html>
<head>
  <title>KrishiMitra WhatsApp QR Code</title>
  <meta http-equiv="refresh" content="30">
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; text-align: center; padding: 50px; background-color: #f0f2f5; }
    .card { background: white; padding: 40px; border-radius: 12px; display: inline-block; box-shadow: 0 4px 12px rgba(0,0,0,0.08); max-width: 420px; }
    img { margin-top: 25px; border: 1px solid #e1e4e8; padding: 15px; background: white; border-radius: 8px; }
    h1 { color: #075e54; margin-bottom: 8px; font-size: 24px; }
    p { color: #4a4a4a; font-size: 15px; line-height: 1.4; margin: 0; }
    .badge { background: #d9fdd3; color: #075e54; font-weight: bold; font-size: 12px; padding: 4px 12px; border-radius: 20px; display: inline-block; margin-bottom: 15px; }
    .footer { margin-top: 20px; font-size: 12px; color: #888; }
  </style>
</head>
<body>
  <div class="card">
    <div class="badge">🌾 KrishiMitra AI WhatsApp Gateway</div>
    <h1>Scan QR Code to Connect</h1>
    <p>Open WhatsApp on your phone, go to <strong>Linked Devices</strong>, and scan the QR code below to activate your phone as the KrishiMitra WhatsApp Bot.</p>
    <img src="https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${encodeURIComponent(qr)}" alt="WhatsApp QR Code" />
    <div class="footer">This page auto-refreshes every 30 seconds if the code updates.</div>
  </div>
</body>
</html>`;

    const uploadsDir = path.resolve('./uploads');
    if (!fs.existsSync(uploadsDir)) {
      fs.mkdirSync(uploadsDir, { recursive: true });
    }
    const htmlPath = path.join(uploadsDir, 'whatsapp-qr.html');
    fs.writeFileSync(htmlPath, htmlContent);
    console.log(`[QR CODE] Saved QR page to: file://${htmlPath.replace(/\\/g, '/')}`);
    
    // Auto open in default browser on Windows
    if (process.platform === 'win32') {
      exec(`start "" "${htmlPath}"`);
    }
  } catch (err) {
    console.error('Failed to create QR HTML page:', err);
  }
});

client.on('ready', () => {
  console.log('\n====================================================');
  console.log('  ✅ KrishiMitra WhatsApp Bot is Connected & READY!  ');
  console.log('====================================================\n');

  try {
    const htmlPath = path.resolve('./uploads/whatsapp-qr.html');
    if (fs.existsSync(htmlPath)) {
      const htmlContent = `<!DOCTYPE html>
<html>
<head>
  <title>KrishiMitra WhatsApp Gateway Connected</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; text-align: center; padding: 100px 50px; background-color: #f0f2f5; }
    .card { background: white; padding: 40px; border-radius: 12px; display: inline-block; box-shadow: 0 4px 12px rgba(0,0,0,0.08); max-width: 420px; }
    h1 { color: #075e54; font-size: 28px; margin-bottom: 10px; }
    p { color: #4a4a4a; font-size: 16px; line-height: 1.4; margin: 0; }
  </style>
</head>
<body>
  <div class="card">
    <h1>✅ Connected & Active!</h1>
    <p>Your WhatsApp account is now linked as the official <strong>KrishiMitra AI Bot</strong>. Incoming questions will be answered automatically!</p>
  </div>
</body>
</html>`;
      fs.writeFileSync(htmlPath, htmlContent);
    }
  } catch (e) {}
});

client.on('message_create', async (msg) => {
  try {
    // Ignore status broadcast and group messages
    if (!msg.from.endsWith('@c.us') && !msg.from.endsWith('@lid')) {
      return;
    }

    // Ignore self messages unless sent to self
    if (msg.fromMe && msg.to !== msg.from) {
      return;
    }

    const fromRaw = msg.from.split('@')[0];
    const userPhone = `+${fromRaw}`;
    const userQuery = msg.body?.trim();

    if (!userQuery) return;

    const isActivation = /krishi\s*mitra|कृषिमित्र|ಕೃಷಿಮಿತ್ರ|கிருஷிமித்ரா/i.test(userQuery);
    console.log(`[INCOMING] Message from ${userPhone}: "${userQuery}" ${isActivation ? '🔔 (Activation Trigger Received)' : ''}`);

    // Call KrishiMitra backend API
    const response = await axios.post(`${BACKEND_URL}/api/query`, {
      text: userQuery
    });

    const replyText = response.data?.text || "Sorry, I could not process your query at the moment. Please try again.";

    console.log(`[OUTGOING] Reply to ${userPhone}: "${replyText.substring(0, 80).replace(/\n/g, ' ')}..."`);
    await msg.reply(replyText);

  } catch (err) {
    console.error(`[ERROR] Failed processing WhatsApp message:`, err.message || err);
    try {
      await msg.reply("🌾 *KrishiMitra AI*:\nSorry, an error occurred while fetching Mandi rates. Please try again shortly.");
    } catch (e) {}
  }
});

client.initialize();
