# 🔐 Setting Up Groq API Key as GitHub Secret

This guide will help you configure the Groq API key as a GitHub Secret so it's automatically injected during deployment.

## Prerequisites

- A Groq API key (get one from [console.groq.com/keys](https://console.groq.com/keys))
- Admin access to your GitHub repository

## Step-by-Step Instructions

### 1. Get Your Groq API Key

1. Go to [https://console.groq.com/keys](https://console.groq.com/keys)
2. Sign in or create an account
3. Click "Create API Key"
4. Copy the key (it starts with `gsk_`)

### 2. Add Secret to GitHub Repository

1. Go to your GitHub repository: [https://github.com/mfmqazi/lmkhealth](https://github.com/mfmqazi/lmkhealth)
2. Click on **Settings** (top navigation)
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Enter the following:
   - **Name:** `GROQ_API_KEY`
   - **Secret:** Paste your Groq API key (e.g., `gsk_...`)
6. Click **Add secret**

### 3. Enable GitHub Pages (if not already enabled)

1. In your repository, go to **Settings** → **Pages**
2. Under **Source**, select:
   - Source: **GitHub Actions**
3. Save the settings

### 4. Deploy

The workflow will automatically trigger on:
- Every push to the `main` branch
- Manual trigger via "Actions" tab → "Deploy to GitHub Pages" → "Run workflow"

To deploy now:

```bash
# Commit and push the changes
git add .
git commit -m "Add GitHub Actions deployment with Groq API key"
git push origin main
```

The deployment will:
1. Build the frontend with the Groq API key injected
2. Deploy to GitHub Pages at: https://mfmqazi.github.io/lmkhealth/

### 5. Verify Deployment

1. Go to the **Actions** tab in your GitHub repository
2. Watch the workflow run (should take 1-2 minutes)
3. Once complete, visit: https://mfmqazi.github.io/lmkhealth/
4. Click "Summarize" on any transcript - it should work without asking for a key!

## Local Development

For local development, create a `.env` file in `src/frontend/`:

```bash
cd src/frontend
cp .env.example .env
```

Then edit `.env` and add your key:

```env
VITE_GROQ_API_KEY=gsk_your_actual_key_here
```

**Important:** The `.env` file is gitignored and will NOT be committed to the repository.

## How It Works

1. **Build Time:** During GitHub Actions build, the `GROQ_API_KEY` secret is injected as `VITE_GROQ_API_KEY` environment variable
2. **Vite Config:** The `vite.config.js` exposes this as `import.meta.env.VITE_GROQ_API_KEY`
3. **App.jsx:** The app checks for the build-time key first, then falls back to localStorage
4. **Result:** Users don't need to enter a key - it's already embedded in the deployed app!

## Fallback Behavior

If no build-time key is available:
- Users can still add their own key via the Settings modal
- The key is stored in browser localStorage
- This is useful for local development or if you want users to use their own keys

## Security Notes

✅ **Safe:**
- GitHub Secrets are encrypted and only accessible during workflow runs
- The key is embedded in the built JavaScript (public, but that's expected for client-side apps)
- This is the standard approach for client-side API keys

⚠️ **Important:**
- Anyone can view the key by inspecting the deployed JavaScript
- Use Groq's rate limiting and monitoring features
- Consider using Groq's API key restrictions if available

## Troubleshooting

**Workflow fails:**
- Check that the secret name is exactly `GROQ_API_KEY` (case-sensitive)
- Verify the secret is set in the correct repository

**Summarization doesn't work:**
- Check browser console for errors
- Verify the deployment completed successfully
- Try clearing browser cache and reloading

**Need to update the key:**
1. Go to Settings → Secrets and variables → Actions
2. Click on `GROQ_API_KEY`
3. Click "Update secret"
4. Enter the new key and save
5. Re-run the workflow or push a new commit

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Groq API Documentation](https://console.groq.com/docs)
