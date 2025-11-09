# Search Index Quick Reference

This guide shows you how to manage the automated search index for your neuroscience learning platform.

## 🎯 Quick Overview

The search system **automatically** extracts metadata from your Vue pages and generates a searchable index. No more manual maintenance!

## 📝 When You Add a New Page

### Step 1: Add `pageMetadata` to Your Vue Component

Every searchable page should include this in the `<script setup>` section:

```vue
<script setup lang="ts">
const pageMetadata = {
  id: 'unique-page-id',              // e.g., 'topic3-page2'
  title: 'Your Page Title',          // What appears in search results
  content: 'Full text description of your page content that will be searched',
  excerpt: 'Brief 1-2 sentence summary for search results preview',
  path: '/your/route/path',          // Must match your router path
  tags: ['tag1', 'tag2', 'concept'], // Searchable keywords
  category: 'Category Name',         // e.g., 'Neuroscience', 'Senses', 'Help'
  type: 'page' as const,
  metadata: {
    chapter: 'Chapter 3',            // Optional: Chapter name
    difficulty: 'beginner' as const, // 'beginner' | 'intermediate' | 'advanced'
    estimatedReadTime: 10            // Optional: Minutes to read
  }
}
</script>
```

### Step 2: Update the Search Index

**Option A - Automatic (Recommended)**
```bash
yarn build  # Index regenerates automatically
```

**Option B - Manual**
```bash
yarn generate-search-index
```

That's it! Your page is now searchable.

## 🔄 Automatic Updates

The search index is **automatically regenerated** when you:
- Run `yarn build` (production builds)
- Run `yarn generate-search-index` manually

**Note:** During `yarn dev`, the index is NOT auto-regenerated. Run the manual command if you need to test search during development.

## 📋 Complete Example

Here's a real example from the codebase:

```vue
<script setup lang="ts">
const pageMetadata = {
  id: 'topic1-page1',
  title: 'Visual receptors and retinal interaction',
  content: 'The Nobel Prize in Physiology or Medicine in 1967 was awarded jointly to Haldan Keffer Hartline, Ragnar Granit, and George Wald for their discoveries concerning visual processes.',
  excerpt: 'the basic mechanism of the receptor is one that emphasizes change.',
  path: '/topic1/page1',
  tags: ['model organisms', 'vision', 'retina', 'lateral-inhibition'],
  category: 'Senses',
  type: 'page' as const,
  metadata: {
    chapter: 'Chapter 1',
    difficulty: 'beginner' as const,
    estimatedReadTime: 12
  }
}
</script>

<template>
  <div class="page-container">
    <!-- Your page content -->
  </div>
</template>
```

## 🎨 Search Features

Your users can search by:
- **Page titles** (40% weight)
- **Content descriptions** (30% weight)
- **Tags** (20% weight)
- **Categories** (10% weight)

The search uses fuzzy matching, so typos and partial matches work!

## ⚙️ Generated Files

**DO NOT EDIT MANUALLY:**
- `src/utilities/searchUtils.ts` - Auto-generated search index and functions

**Safe to Edit:**
- `scripts/generate-search-index.js` - The generator script
- Your Vue page files with `pageMetadata`

## 🐛 Troubleshooting

### Page Not Showing in Search

1. ✅ Confirm `pageMetadata` exists in your Vue file
2. ✅ Check that `id`, `title`, and `path` are provided
3. ✅ Run `yarn generate-search-index`
4. ✅ Check terminal output for errors or warnings

### Script Output Shows "Skipped"

The page doesn't have a `pageMetadata` object. Pages without metadata won't be searchable (this is intentional for pages like the homepage).

### Search Not Working After Updates

```bash
# Regenerate the index
yarn generate-search-index

# If using dev server, restart it
yarn dev
```

## 📊 Check What's Indexed

Run the generator to see a summary:

```bash
yarn generate-search-index
```

Output example:
```
✨ Successfully generated search index!
📊 Total entries: 4

📋 Breakdown by category:
   • Neuroscience: 2 pages
   • Senses: 1 page
   • Help: 1 page
```

## 💡 Tips

1. **Use descriptive tags** - These help users find content with keyword searches
2. **Write clear excerpts** - This appears in search results
3. **Fill in the content field** - This is what gets searched, make it comprehensive
4. **Choose appropriate difficulty** - Helps users find content at their level
5. **Keep paths consistent** - Must match your router configuration

## 🚀 Integration with Build Process

The search index generation is integrated into your build pipeline:

```json
{
  "scripts": {
    "build": "node scripts/generate-search-index.js && vite build"
  }
}
```

Every production build automatically has an up-to-date search index!

## 📚 Further Documentation

- Full details: `scripts/README.md`
- Architecture: `CLAUDE.md` (Search System section)
- Type definitions: `src/types/search.ts`
