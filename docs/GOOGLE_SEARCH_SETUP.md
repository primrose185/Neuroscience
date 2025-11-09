# Google Custom Search Setup Guide

## Step 1: Create a Programmable Search Engine

1. **Go to Google Programmable Search Engine Console:**
   - Visit: https://programmablesearchengine.google.com/
   - Sign in with your Google account

2. **Create a New Search Engine:**
   - Click "Add" or "Create a custom search engine"
   - **Name your search engine:** "nREM Neuroscience Search" (or any name you prefer)
   - **What to search:**
     - For development/testing: Enter `*.yourdomain.com/*` (replace with your actual domain)
     - Or enter specific URLs you want to search
     - You can also select "Search the entire web" initially and restrict it later
   - Click "Create"

3. **Get Your Search Engine ID:**
   - After creation, you'll see your Search Engine ID (starts with a long string like `a1b2c3d4e5f6g7h8i`)
   - **Copy this ID** - you'll need it for the code

4. **Customize Your Search Engine (Optional):**
   - Go to "Look and feel" to customize colors and layout
   - Go to "Setup" to add or remove sites to search
   - Go to "Search features" to enable image search, autocomplete, etc.

## Step 2: Get Your Code

1. **Navigate to the "Overview" section**
2. Click on "Get code"
3. You'll see two options:
   - **Two-page** (search box on one page, results on another)
   - **Results only** (just results, you provide the search box)
   - **Two-column** (search box and results on same page)

4. Choose **"Two-column"** or **"Results only"** depending on your preference

## Step 3: Copy Your Search Engine ID

You'll need to add your Search Engine ID to the application:

1. The ID will be in the code snippet as: `cx = 'YOUR_SEARCH_ENGINE_ID'`
2. Copy this ID

## Step 4: Add to Your Application

Create a `.env.local` file in your project root:

```bash
VITE_GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
```

**Important:**
- Don't commit `.env.local` to git (it's already in `.gitignore`)
- For production deployment on Vercel, add this as an environment variable in your Vercel project settings

## Configuration Options

### Search Features You Can Enable:

1. **Image Search** - Include image results
2. **SafeSearch** - Filter explicit content
3. **Autocomplete** - Suggest queries as users type
4. **Synonyms** - Include related terms in search
5. **Promotions** - Highlight specific pages for certain queries

### Appearance Customization:

1. **Themes** - Choose from pre-built themes or customize colors
2. **Layout** - Full-width, two-column, overlay, etc.
3. **Font** - Match your site's typography
4. **Custom CSS** - Advanced styling options

## Limits and Pricing

### Free Tier:
- **100 queries per day** for free
- Ads will be shown in search results (can't be removed on free tier)

### Paid Tier (Custom Search JSON API):
- **10,000 queries per day** for $5/month
- Can remove ads
- Requires API key from Google Cloud Console
- More customization options

## Alternative: Using the API (Advanced)

If you need more control or want to remove ads:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project
3. Enable "Custom Search API"
4. Create credentials (API key)
5. Use the API endpoint instead of embedded widget

**API Endpoint:**
```
https://www.googleapis.com/customsearch/v1?key=YOUR_API_KEY&cx=YOUR_SEARCH_ENGINE_ID&q=QUERY
```

## Testing

1. Once configured, test on localhost first
2. The search will work on localhost but results will be limited to your configured sites
3. After deployment, update your search engine to include your production domain

## Troubleshooting

**Search not showing results:**
- Make sure your site is indexed by Google (can take a few days for new sites)
- Check your search engine's "Sites to search" configuration
- Try "Search the entire web" mode initially for testing

**"This site can't be reached" error:**
- Your domain isn't added to the allowed sites in the search engine setup
- Add `localhost:5173` for local development

**Styling issues:**
- The widget inherits some CSS from your site
- Use the "Look and feel" customization in the Google console
- Or add custom CSS overrides in your component

## Next Steps

After completing the setup:
1. Add your Search Engine ID to `.env.local`
2. The GoogleSearchBar component is already created and integrated
3. Test locally with `yarn dev`
4. Deploy to Vercel and add the environment variable there
