# KrishiMitra AI Platform Deployment Guide

Since this platform has two parts—a **Next.js frontend web server** and a **Flask backend server with SQLite**—it cannot be hosted on static cloud storage like Google Drive (which doesn't run Python or Node.js execution environments).

Instead, you can host both the frontend and backend for **free** in under 10 minutes using modern cloud hosting platforms like **Vercel** and **Render** (or **PythonAnywhere**). This guide explains how to set it up so you can share it with your friends for testing.

---

## Step 1: Upload Your Code to GitHub (Prerequisite)

Vercel and Render sync directly with GitHub. To start:
1. Create a free account on [GitHub](https://github.com/).
2. Push your project folder (`c:\Ajit\Work\Website\Agriculture`) to a public or private GitHub repository.

---

## Step 2: Deploy the Backend (Flask API) on Render

[Render](https://render.com/) offers free Python hosting.

1. **Sign Up**: Log in to Render using your GitHub account.
2. **Create Web Service**: Click **New +** -> **Web Service**.
3. **Link Repo**: Select your KrishiMitra GitHub repository.
4. **Configure Settings**:
   - **Name**: `krishimitra-backend`
   - **Root Directory**: `backend` (Important: points to your Flask server subdirectory)
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app.main:app` (Gunicorn is the production WSGI server for Flask)
5. **Environment Variables**: Click **Advanced** -> **Add Environment Variable**:
   - `GEMINI_API_KEY`: *(Optional: Your Google AI Studio Key)*
   - `TWILIO_AUTH_TOKEN`: *(Optional: Your Twilio webhook key)*
   - `FRONTEND_APP_URL`: *(Your Vercel URL, which you will generate in Step 3)*
6. **Deploy**: Click **Create Web Service**. Render will build and deploy the API, providing you with a public URL like `https://krishimitra-backend.onrender.com`.

---

## Step 3: Deploy the Frontend (Next.js) on Vercel

[Vercel](https://vercel.com/) is the creator of Next.js and provides free high-performance hosting.

1. **Sign Up**: Log in to Vercel using your GitHub account.
2. **Import Project**: Click **Add New** -> **Project** and select your KrishiMitra repository.
3. **Configure Settings**:
   - **Framework Preset**: `Next.js`
   - **Root Directory**: Click Edit and select the `frontend` folder (Important: points to your Next.js subdirectory).
4. **Environment Variables**: Add this variable to link the frontend to your Render backend:
   - **Name**: `NEXT_PUBLIC_BACKEND_URL`
   - **Value**: `https://krishimitra-backend.onrender.com` *(Use the URL generated in Step 2)*
5. **Deploy**: Click **Deploy**. Vercel will compile the Next.js app and give you a public URL like `https://krishimitra.vercel.app`!

---

## Sharing with Friends
- Give your friends the Vercel link (`https://krishimitra.vercel.app`).
- They can open it on their computers, tablets, or phones!
- They will be able to test the **dropdown mandi prices**, the **marketplace directory**, and use their **real microphone** to ask questions in English, Hindi, or Kannada directly!
