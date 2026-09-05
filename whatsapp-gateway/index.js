const { Client, LocalAuth, MessageMedia } = require('whatsapp-web.js');
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

async function fetchVoiceNoteMedia(client, msg) {
  for (let attempt = 1; attempt <= 4; attempt++) {
    // 1. Reload message model and try native downloadMedia
    try {
      try { await msg.reload(); } catch (e) {}
      const media = await msg.downloadMedia();
      if (media && media.data) return media;
    } catch (err) {
      console.log(`[VOICE NOTE ATTEMPT ${attempt}] Native downloadMedia failed: ${err.message || String(err)}`);
    }

    // 2. Direct browser context media resolution via window.Store & mediaBlob fallback
    try {
      const msgIdSerialized = msg.id && msg.id._serialized ? msg.id._serialized : null;
      if (msgIdSerialized) {
        const bRes = await client.pupPage.evaluate(async (msgId) => {
          try {
            // Safely locate Store message model
            const MsgStore = window.Store ? window.Store.Msg : (window.require ? window.require('WAWebCollections')?.Msg : null);
            if (!MsgStore) return { error: 'MsgStore is not accessible in browser' };

            let m = MsgStore.get(msgId);
            if (!m && MsgStore.getMessagesById) {
              const fetched = await MsgStore.getMessagesById([msgId]);
              m = fetched?.messages?.[0];
            }
            if (!m) return { error: 'Message not found in Store' };

            // Trigger download if media stage is not resolved
            if (m.mediaData && m.mediaData.mediaStage !== 'RESOLVED') {
              try {
                await m.downloadMedia({ downloadEvenIfExpensive: true, rmrReason: 1 });
              } catch (e) {}
            }

            // Poll up to 10 iterations (5 seconds) for media download completion
            for (let i = 0; i < 10; i++) {
              if (m.mediaData && (m.mediaData.mediaStage === 'RESOLVED' || m.mediaData.mediaStage === 'FETCHED')) {
                break;
              }
              await new Promise(r => setTimeout(r, 500));
            }

            let decrypted = null;
            const dlMgr = window.Store ? window.Store.DownloadManager : null;
            const mockQpl = { addAnnotations: function () { return this; }, addPoint: function () { return this; } };
            const targetType = (m.type === 'ptt' || m.type === 'audio') ? 'audio' : m.type;

            if (dlMgr && dlMgr.downloadAndMaybeDecrypt) {
              try {
                decrypted = await dlMgr.downloadAndMaybeDecrypt({
                  directPath: m.directPath,
                  encFilehash: m.encFilehash,
                  filehash: m.filehash,
                  mediaKey: m.mediaKey,
                  mediaKeyTimestamp: m.mediaKeyTimestamp,
                  type: targetType,
                  signal: new AbortController().signal,
                  downloadQpl: mockQpl,
                });
              } catch (e) {}
            }

            // Fallback: Read arrayBuffer directly from resolved mediaBlob
            if (!decrypted && m.mediaData && m.mediaData.mediaBlob) {
              try {
                decrypted = await m.mediaData.mediaBlob.arrayBuffer();
              } catch (e) {}
            }

            if (!decrypted) return { error: 'Media buffer resolution returned empty' };
            const dataB64 = await window.WWebJS.arrayBufferToBase64Async(decrypted);
            return {
              data: dataB64,
              mimetype: m.mimetype || 'audio/ogg',
              filename: m.filename || 'audio.ogg'
            };
          } catch (e) {
            return { error: e.message || String(e) };
          }
        }, msgIdSerialized);

        if (bRes && bRes.data) {
          return new MessageMedia(bRes.mimetype, bRes.data, bRes.filename);
        } else if (bRes && bRes.error) {
          console.log(`[VOICE NOTE BROWSER STORE WARN ${attempt}] ${bRes.error}`);
        }
      }
    } catch (e) {
      console.log(`[VOICE NOTE EVAL WARN ${attempt}] ${e.message || String(e)}`);
    }

    await new Promise(r => setTimeout(r, 1000));
  }

  return null;
}


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

    // 1. Handle Voice Note / Audio Messages
    if (msg.hasMedia && (msg.type === 'ptt' || msg.type === 'audio')) {
      console.log(`[INCOMING VOICE NOTE] Voice note received from ${userPhone}... preparing audio download`);
      try {
        const media = await fetchVoiceNoteMedia(client, msg);

        if (media && media.data) {
          console.log(`[VOICE NOTE DOWNLOADED] Size: ${media.data.length} chars, Mime: ${media.mimetype}`);
          
          const axiosConfig = {
            timeout: 25000,
            maxBodyLength: Infinity,
            maxContentLength: Infinity
          };

          let response;
          try {
            response = await axios.post(`http://127.0.0.1:8000/api/query/voice`, {
              audio: media.data,
              mime_type: media.mimetype || 'audio/ogg'
            }, axiosConfig);
          } catch (e1) {
            response = await axios.post(`http://localhost:8000/api/query/voice`, {
              audio: media.data,
              mime_type: media.mimetype || 'audio/ogg'
            }, axiosConfig);
          }

          const replyText = response.data?.text?.trim() || "";
          const transcribed = response.data?.transcribed_text || "Voice Note";
          const audioB64 = response.data?.audio_base64;
          
          if (!replyText) {
            console.log(`[SILENT VOICE NOTE] "${transcribed}" from ${userPhone} (No activation phrase or query -> Remaining silent)`);
            return;
          }

          console.log(`[TRANSCRIPTION] "${transcribed}" -> Reply: "${replyText.substring(0, 80).replace(/\n/g, ' ')}..."`);
          await msg.reply(`🎤 *Voice Note Transcribed* ("${transcribed}"):\n\n${replyText}`);

          if (audioB64) {
            try {
              const voiceMedia = new MessageMedia('audio/mp3', audioB64, 'krishimitra_reply.mp3');
              await client.sendMessage(msg.from, voiceMedia, { sendAudioAsVoice: true });
              console.log(`[VOICE PLAYBACK] Sent audio voice reply to ${userPhone}`);
            } catch (aErr) {
              console.error(`[VOICE PLAYBACK ERROR] ${aErr.message || aErr}`);
            }
          }
          return;
        } else {
          console.log(`[VOICE NOTE WARN] Failed downloading media buffer for ${userPhone}`);
        }
      } catch (voiceErr) {
        const vErrStr = (voiceErr && voiceErr.message) ? voiceErr.message : String(voiceErr);
        console.error(`[VOICE NOTE ERROR] Audio processing failed: ${vErrStr}`);
        try {
          await msg.reply("🌾 *KrishiMitra AI*:\nAudio voice note received. Could not transcribe audio. Please try speaking clearly or send as text query.");
        } catch (e) {}
        return;
      }
    }

    // 2. Handle Text Messages
    const userQuery = msg.body?.trim();
    if (!userQuery) return;

    const isActivation = /krishi\s*mitra|कृषिमित्र|ಕೃಷಿಮಿತ್ರ|கிருஷிமித்ரா/i.test(userQuery);
    console.log(`[INCOMING TEXT] Message from ${userPhone}: "${userQuery}" ${isActivation ? '🔔 (Activation Trigger Received)' : ''}`);

    let response;
    try {
      response = await axios.post(`http://127.0.0.1:8000/api/query`, { text: userQuery }, { timeout: 20000 });
    } catch (e1) {
      response = await axios.post(`http://localhost:8000/api/query`, { text: userQuery }, { timeout: 20000 });
    }

    const replyText = response.data?.text?.trim() || "";
    const audioB64 = response.data?.audio_base64;

    if (!replyText) {
      console.log(`[SILENT TEXT] Message from ${userPhone}: "${userQuery}" (No activation phrase -> Remaining silent)`);
      return;
    }

    console.log(`[OUTGOING REPLY] Reply to ${userPhone}: "${replyText.substring(0, 80).replace(/\n/g, ' ')}..."`);
    await msg.reply(replyText);

    if (audioB64 && isActivation) {
      try {
        const voiceMedia = new MessageMedia('audio/mp3', audioB64, 'krishimitra_reply.mp3');
        await client.sendMessage(msg.from, voiceMedia, { sendAudioAsVoice: true });
        console.log(`[VOICE PLAYBACK] Sent audio voice reply to ${userPhone}`);
      } catch (aErr) {
        console.error(`[VOICE PLAYBACK ERROR] ${aErr.message || aErr}`);
      }
    }

  } catch (err) {
    const mainErrStr = (err && err.message) ? err.message : String(err);
    console.error(`[ERROR] Failed processing WhatsApp message: ${mainErrStr}`);
    try {
      await msg.reply("🌾 *KrishiMitra AI*:\nBackend server connection error. Please make sure the Python server (`python app/main.py`) is running on port 8000.");
    } catch (e) {}
  }
});

client.initialize();
