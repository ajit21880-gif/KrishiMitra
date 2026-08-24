# KrishiMitra AI - API Linking Guide

This guide details step-by-step instructions on how to obtain official Government Mandi data API keys, WhatsApp Business API credentials, and Google Gemini AI keys, and how to link them in this codebase for live production.

---

## 1. Official Government Mandi Prices (data.gov.in / AGMARKNET)

The Government of India hosts official data feeds on the Open Government Data (OGD) platform. Daily wholesale mandi rates are published through the **Agmarknet** portal.

### Steps to obtain the API key:
1. Visit the Open Government Data Portal: [https://data.gov.in/](https://data.gov.in/)
2. Click on **Register** at the top right to create a developer account. Fill in the required fields (Name, Email, Mobile).
3. Verify your registration using the link sent to your email.
4. Log in to [data.gov.in](https://data.gov.in/).
5. Go to your profile menu (top right) and click on **My API Keys** or **My Account -> API Credentials**.
6. Click **Generate New API Key** and copy the long alphabetic-numeric string.
7. Search the portal for the resource ID: `9ef84281-22f3-497d-aa5d-8c6c52d77290` (this is the official dataset ID for "Daily wholesale prices of agricultural commodities").

### Linking in the Code:
Set the environment variable:
```bash
DATAGOV_API_KEY="your_copied_api_key_here"
```
The codebase (`app/services/mandi_service.py`) automatically intercepts this key, fetches live wholesale feeds, and caches them for 30 minutes to stay within the rate limit.

---

## 2. Google Gemini API Key (Natural Language Processing & Intent Parsing)

We use Google Gemini to automatically transcribe user messages, detect regional Indian languages (Hindi, Kannada, etc.), and classify user intent (e.g. Price lookup vs Fertilizer dealer search).

### Steps to obtain the API key:
1. Go to **Google AI Studio**: [https://aistudio.google.com/](https://aistudio.google.com/)
2. Sign in with your Google account.
3. Click on the **Get API key** button on the left sidebar.
4. Click **Create API Key** (you can link it to an existing Google Cloud project or create a new one).
5. Copy the generated API key.

### Linking in the Code:
Set the environment variable:
```bash
GEMINI_API_KEY="your_gemini_api_key_here"
```
If this key is missing, the codebase uses a regex-based fallback keyword parser to process queries locally.

---

## 3. WhatsApp Business Integration

You can link WhatsApp using either **Twilio** (recommended for easy testing/sandbox) or the **Meta WhatsApp Cloud API** (recommended for production). The codebase supports toggling between both.

### Option A: Twilio Sandbox (Easiest for Developer Testing)
1. Sign up for a Twilio Account: [https://www.twilio.com/](https://www.twilio.com/)
2. On your Twilio Console dashboard, locate and copy:
   - **Account SID**
   - **Auth Token**
3. Navigate to **Messaging -> Try it out -> Send a WhatsApp Message** to activate the Twilio WhatsApp Sandbox.
4. Send the join code (e.g., `join sandbox-name`) from your WhatsApp phone to the sandbox number (usually `+1 415 523 8886`) to register your test phone.
5. In Twilio, configure the **Webhook URL for Incoming Messages** to point to your backend:
   `https://<your-public-url>/api/whatsapp/twilio`

### Option B: Meta WhatsApp Cloud API (Production-Ready)
1. Sign up as a Meta Developer: [https://developers.facebook.com/](https://developers.facebook.com/)
2. Go to **My Apps -> Create App** and select **Business** as the app type.
3. Scroll down and click **Set up** next to the **WhatsApp** product.
4. Under the "Getting Started" tab:
   - Copy the **Temporary Access Token** (for production, generate a Permanent System User Token under Business Settings).
   - Copy the **Phone Number ID**.
5. Under the "Configuration" tab:
   - Click **Edit Webhook**. Set the Callback URL to `https://<your-public-url>/api/whatsapp/webhook`.
   - Set the Verification Token to a secret string of your choice (e.g. `krishimitra_secret_token`).
   - Subscribe to the `messages` webhook field.

### Linking in the Code:
Set the environment variables based on your preferred provider:
```bash
# Toggle between 'twilio' or 'meta'
WHATSAPP_PROVIDER="twilio"

# If using Twilio:
TWILIO_ACCOUNT_SID="your_twilio_sid"
TWILIO_AUTH_TOKEN="your_twilio_token"
TWILIO_WHATSAPP_FROM="whatsapp:+14155238886"

# If using Meta:
META_PHONE_NUMBER_ID="your_meta_phone_id"
META_ACCESS_TOKEN="your_meta_access_token"
META_VERIFY_TOKEN="krishimitra_secret_token"
```

---

## 4. Deploying & Testing Public Webhooks Locally (ngrok)

WhatsApp webhooks require a public HTTPS URL. For local development, you can use a tunneling service like **ngrok** to expose your Flask backend running on port `8000`:

1. Download and install ngrok: [https://ngrok.com/](https://ngrok.com/)
2. Run ngrok on port 8000:
   ```bash
   ngrok http 8000
   ```
3. Copy the secure forwarding URL (e.g. `https://abcd-123.ngrok-free.app`).
4. Set this URL in Meta or Twilio webhooks:
   - Meta: `https://abcd-123.ngrok-free.app/api/whatsapp/webhook`
   - Twilio: `https://abcd-123.ngrok-free.app/api/whatsapp/twilio`
