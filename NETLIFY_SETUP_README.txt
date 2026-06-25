NETLIFY SETUP - NO TERMINAL NEEDED

1. Upload this project to Netlify.
   Best option: connect it to GitHub and deploy the repo.
   If you already have a Netlify site, replace the existing site files with this version.

2. Add Kimberly's API key in Netlify:
   Netlify Dashboard > Your Site > Site configuration > Environment variables
   Add:
   OPENAI_API_KEY = Kimberly's API key
   DEMO_MODE = false
   OPENAI_CHAT_MODEL = gpt-4o-mini

3. Redeploy the site:
   Deploys > Trigger deploy > Deploy site

4. Open the AI Coach page and test:
   Ask: What is the Legendary Mindset?

IMPORTANT:
- Do NOT put the API key in ai-coach.js.
- The API key only goes in Netlify Environment Variables.
- The AI Coach page calls /.netlify/functions/chat.
