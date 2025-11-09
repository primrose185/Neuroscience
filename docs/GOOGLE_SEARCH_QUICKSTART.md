# Google Search Integration - Quick Start

## ✅ What's Been Implemented

Your neuroscience learning platform now has **dual search functionality**:

1. **📚 Local Search** - Instant search using Fuse.js (your existing search)
2. **🔍 Google Search** - Full Google search embedded in your sidebar

Users can toggle between them with a simple button in the sidebar.

## 🚀 Setup (5 Minutes)

### Step 1: Create Google Programmable Search Engine

1. Visit: https://programmablesearchengine.google.com/
2. Click **"Add"** or **"Create"**
3. Fill in:
   - **Name**: "nREM Neuroscience Search" (or your preference)
   - **What to search**:
     - For now, select **"Search the entire web"**
     - After deployment, you can restrict to your domain
4. Click **"Create"**
5. **Copy your Search Engine ID** (looks like: `a1b2c3d4e5f6g7h8i`)

### Step 2: Add to Your Project

Create a file named `.env.local` in your project root:

```bash
VITE_GOOGLE_SEARCH_ENGINE_ID=paste_your_id_here
```

**Example:**
```bash
VITE_GOOGLE_SEARCH_ENGINE_ID=a1b2c3d4e5f6g7h8i
```

### Step 3: Test Locally

```bash
yarn dev
```

Visit http://localhost:5173 and you should see:
- A toggle button in the sidebar: **📚 Local** | **🔍 Google**
- Click "Google" to switch to Google search
- Try a search!

### Step 4: Deploy to Vercel

1. **Push your code** to GitHub (the `.env.local` file won't be committed - it's in `.gitignore`)

2. **Add environment variable in Vercel**:
   - Go to your Vercel project dashboard
   - Settings → Environment Variables
   - Add: `VITE_GOOGLE_SEARCH_ENGINE_ID` = `your_id_here`
   - Apply to: Production, Preview, and Development

3. **Redeploy** your site

4. **(Optional) Restrict search to your domain**:
   - Go back to https://programmablesearchengine.google.com/
   - Select your search engine
   - Go to "Setup" → "Sites to search"
   - Remove "Search the entire web"
   - Add your Vercel domain (e.g., `yoursite.vercel.app`)

## 📱 How It Works

### User Experience

1. User opens your site
2. Sidebar shows search with toggle: **📚 Local** | **🔍 Google**
3. Default is Local Search (instant, no page refresh)
4. Clicking **🔍 Google** switches to Google's embedded search
5. Results appear directly in your sidebar - no redirects!

### Technical Details

**Files Created:**
- `src/components/GoogleSearchBar.vue` - Google search component
- `GOOGLE_SEARCH_SETUP.md` - Detailed setup guide
- `.env.example` - Environment variable template

**Files Modified:**
- `src/components/Sidebar.vue` - Added search mode toggle
- `CLAUDE.md` - Updated documentation

**What Happens:**
1. Component loads Google's CSE script dynamically
2. Script reads your Search Engine ID from environment variables
3. Google renders their search widget in your component
4. Results appear inline (no page navigation)

## 🎨 Customization

### Change Search Appearance

1. Go to https://programmablesearchengine.google.com/
2. Select your search engine
3. Click **"Look and feel"**
4. Customize:
   - Layout (Full width, Two column, Compact, etc.)
   - Themes and colors
   - Fonts
   - Custom CSS

The widget will automatically update on your site!

### Modify Toggle Buttons

Edit `src/components/Sidebar.vue` - Search for `.mode-button` styles to change colors, fonts, icons, etc.

## 💡 Tips

### Search Performance

- **Local Search**: Instant, works offline, limited to your indexed content
- **Google Search**: Broader results, requires internet, includes web content

### When to Use Each

**Use Local Search:**
- Quick lookups of your site content
- Finding specific topics/articles
- Offline functionality
- Privacy (no external requests)

**Use Google Search:**
- Finding related web resources
- More comprehensive results
- External references
- User wants Google's ranking/relevance

### SEO Optimization

To make Google search work better on your site:
1. Add a `sitemap.xml`
2. Submit to Google Search Console
3. Ensure pages are indexed (takes a few days for new sites)
4. Add structured data to your pages

## 🔧 Troubleshooting

### "Google Search not configured" message appears

**Problem**: Environment variable not set
**Solution**: Create `.env.local` with your Search Engine ID

### Search widget doesn't load

**Problem**: Invalid Search Engine ID or script blocked
**Solution**:
- Check your ID is correct
- Ensure no ad blockers are interfering
- Check browser console for errors

### No results showing

**Problem**: Google hasn't indexed your site yet
**Solution**:
- Use "Search the entire web" mode initially
- Submit your site to Google Search Console
- Wait a few days for indexing
- Check your site is publicly accessible

### Widget looks weird / styling issues

**Problem**: CSS conflicts
**Solution**: Check `GoogleSearchBar.vue` `:deep()` styles and adjust

## 📊 Limits

### Free Tier
- ✅ **100 searches per day**
- ✅ Free forever
- ⚠️ Ads shown in results (can't remove)

### Paid Tier ($5/month)
- ✅ **10,000 searches per day**
- ✅ Remove ads
- ✅ More customization
- Requires Custom Search JSON API setup

## 📚 Documentation

- **Detailed Setup**: See `GOOGLE_SEARCH_SETUP.md`
- **Component Code**: `src/components/GoogleSearchBar.vue`
- **Architecture**: Updated in `CLAUDE.md`

## ✨ Next Steps

1. Set up your Search Engine ID (5 minutes)
2. Test locally
3. Deploy to Vercel with environment variable
4. Customize appearance in Google Console
5. (Optional) Restrict to your domain after deployment
6. (Optional) Add sitemap and submit to Search Console

**That's it! Your users now have powerful dual search functionality.** 🎉
