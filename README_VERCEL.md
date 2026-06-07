# 🚀 Project Caligula: Vercel Serverless Deployment Guide

Welcome! This guide explains exactly how to deploy your handcrafted quantamental platform onto Vercel's edge network under your own custom domain, completely bypassing the Streamlit framework.

Vercel will compile your static HTML/JS frontend instantly and mount your core Python scoring model inside **Vercel Serverless Functions** (running in the cloud) under `/api/*`.

---

## 🔒 Prerequisites & Environment Variables

Public SEC data queries require you to declare a custom User Agent to comply with regulatory rate limits. Before deploying, ensure you have these two variables ready:

1. **`SEC_USER_AGENT`** (Required): Any unique string containing your name and email (e.g. `Your Name your.email@example.com`). The SEC will block requests if this is empty.
2. **`GEMINI_API_KEY`** (Optional): Your Google Gemini REST API key. If omitted, Caligula's **statistical fallback engine** will automatically engage to generate realistic parameters, ensuring the application remains 100% robust and crash-free.

---

## 🗺️ Method A: Deploy via GitHub (Recommended & Easiest)

Connecting your GitHub repository directly to Vercel is the easiest method. Every time you push a code change to your GitHub main branch, Vercel will automatically rebuild and update your live website!

### Step 1: Push Your Code to GitHub
If you haven't already, initialize your Git repository, commit your files, and push them to a public or private GitHub repository:
```bash
git init
git add .
git commit -m "Vercel Migration Complete"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_name.git
git push -u origin main
```

### Step 2: Import into Vercel
1. Go to your [Vercel Dashboard](https://vercel.com/dashboard) (log in with your GitHub account).
2. Click **Add New...** and select **Project**.
3. Select your `project-caligula` repository from the list and click **Import**.

### Step 3: Configure Environment Variables
1. Scroll down to the **Environment Variables** accordion section.
2. Add your environment key-value pairs:
   * **Key**: `SEC_USER_AGENT` | **Value**: `Your Name your.email@example.com`
   * **Key**: `GEMINI_API_KEY` | **Value**: `your_gemini_api_key_here`
3. Click **Add** for each variable.

### Step 4: Deploy!
Click the blue **Deploy** button. Vercel will download your packages, compile your FastAPI Python serverless endpoints, and serve your beautiful Garamond front-end in less than a minute!

---

## 💻 Method B: Deploy from Terminal (Vercel CLI)

If you prefer not to use GitHub, you can deploy the app directly from your terminal using Vercel's Command Line Interface.

### Step 1: Install the Vercel CLI
Ensure you have Node.js installed on your machine, then run:
```bash
npm install -g vercel
```

### Step 2: Link and Configure Your Project
Run the login and setup commands inside your project root directory:
```bash
vercel login
```
Follow the browser prompts to authenticate. Once logged in, run:
```bash
vercel
```
Vercel will prompt you with a series of simple questions:
1. *Set up and deploy "~/project-caligula"?* ──► **Yes**
2. *Which scope do you want to deploy to?* ──► **Select your account**
3. *Link to existing project?* ──► **No**
4. *What's your project's name?* ──► Press Enter to accept `project-caligula`
5. *In which directory is your code located?* ──► Press Enter to accept `./`

### Step 3: Add Your Environment Variables
To set up your User Agent and API keys via the CLI, run:
```bash
vercel env add SEC_USER_AGENT "Your Name your.email@example.com"
vercel env add GEMINI_API_KEY "your_gemini_api_key_here"
```

### Step 4: Publish to Production
To push your deployment live, run:
```bash
vercel --prod
```
The CLI will upload your files, deploy them, and paste your live, production-grade URL directly into your terminal!

---

## 🌐 Binding Your Custom Domain

Once your project is deployed on Vercel, you can bind it to your own custom domain (e.g. `investwithsnp.vercel.app` or a custom `.com`/`.app` domain):

1. Inside your Vercel project panel, go to **Settings** and click the **Domains** tab.
2. Type in your custom domain name (e.g. `investwithsnp.com` or `caligula.yourdomain.com`) and click **Add**.
3. Vercel will automatically configure a **free SSL certificate** (HTTPS) and show you the exact DNS records (CNAME or A records) to paste into your domain registrar (GoDaddy, Namecheap, Google Domains).
4. Once registrar propagation is complete (typically 5 to 15 minutes), your beautiful quantamental research engine will be live for recruiters, portfolio managers, and academic peers worldwide!
