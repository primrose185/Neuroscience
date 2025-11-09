# Search Index Generator

This directory contains scripts for automatically generating the search index used by the application's search functionality.

## Overview

The search system uses **Fuse.js** for fuzzy searching. Instead of manually maintaining a search index, we automatically extract metadata from Vue page components and generate the search index.

## How It Works

### 1. Page Metadata

Each searchable Vue page should include a `pageMetadata` object in its `<script setup>` section:

```typescript
const pageMetadata = {
  id: 'unique-page-id',
  title: 'Page Title',
  content: 'Full description of the page content for searching',
  excerpt: 'Short summary shown in search results',
  path: '/route/to/page',
  tags: ['tag1', 'tag2', 'tag3'],
  category: 'Category Name',
  type: 'page' as const,
  metadata: {
    chapter: 'Chapter 1',
    difficulty: 'beginner' as const,  // 'beginner' | 'intermediate' | 'advanced'
    estimatedReadTime: 10  // in minutes
  }
}
```

### 2. Automatic Extraction

The `generate-search-index.js` script:
1. Scans all `.vue` files in `src/pages/`
2. Extracts the `pageMetadata` object from each file
3. Generates `src/utilities/searchUtils.ts` with all the searchable content
4. Creates search functions using Fuse.js

### 3. Search Weights

The search algorithm uses weighted scoring:
- **Title**: 40% weight
- **Content**: 30% weight
- **Tags**: 20% weight
- **Category**: 10% weight

## Usage

### Manual Update

Run the script manually whenever you add or modify page metadata:

```bash
yarn generate-search-index
# or
node scripts/generate-search-index.js
```

### Automatic Update

The search index is automatically regenerated before each production build:

```bash
yarn build  # Runs generate-search-index.js first, then builds
```

### Development Workflow

When adding a new page:

1. **Create the Vue page component** in `src/pages/`
2. **Add the route** in `src/router/index.ts`
3. **Include pageMetadata** in your page component:
   ```vue
   <script setup lang="ts">
   const pageMetadata = {
     id: 'my-new-page',
     title: 'My New Page',
     content: 'Detailed description...',
     excerpt: 'Brief summary...',
     path: '/my-new-page',
     tags: ['tag1', 'tag2'],
     category: 'Category',
     type: 'page' as const,
     metadata: {
       chapter: 'Chapter X',
       difficulty: 'beginner' as const,
       estimatedReadTime: 10
     }
   }
   </script>
   ```
4. **Run the generator** (optional in dev, automatic in build):
   ```bash
   yarn generate-search-index
   ```

## Required Fields

The following fields are **required** for a page to be indexed:
- `id` - Unique identifier
- `title` - Page title
- `path` - Route path

All other fields are optional but recommended for better search results.

## Output

The script generates `src/utilities/searchUtils.ts` with:

- **searchContent** - Array of all searchable pages
- **performSearch(query, limit)** - Main search function
- **getAllContent()** - Get all indexed content
- **getContentByCategory(category)** - Filter by category
- **getContentByTag(tag)** - Filter by tag

## Search Configuration

Search behavior can be customized in the script by modifying `fuseOptions`:

```javascript
const fuseOptions = {
  keys: [
    { name: 'title', weight: 0.4 },
    { name: 'content', weight: 0.3 },
    { name: 'tags', weight: 0.2 },
    { name: 'category', weight: 0.1 }
  ],
  threshold: 0.4,           // Lower = more strict matching (0.0 to 1.0)
  minMatchCharLength: 3,     // Minimum characters to trigger search
  ignoreLocation: true       // Search anywhere in the text
}
```

## Example Output

Running the script will show:

```
🚀 Search Index Generator
==================================================

🔍 Scanning pages directory...

✅ Extracted metadata from Topic1Page1.vue
   → Visual receptors and retinal interaction (/topic1/page1)
✅ Extracted metadata from Topic2Page1.vue
   → Two Ommatidia Lateral Inhibition Simulation (/topic2/page1)

📊 Found 2 pages with metadata

==================================================

✨ Successfully generated search index!
📝 Output: src/utilities/searchUtils.ts
📊 Total entries: 2

📋 Breakdown by category:
   • Neuroscience: 2 pages
```

## Troubleshooting

### Page not appearing in search

1. Check that `pageMetadata` is defined in the Vue file
2. Verify required fields (`id`, `title`, `path`) are present
3. Run `yarn generate-search-index` to update the index
4. Check the script output for warnings or errors

### Search not working after updates

1. Regenerate the search index: `yarn generate-search-index`
2. Restart the dev server: `yarn dev`
3. Clear browser cache if necessary

## Files

- **scripts/generate-search-index.js** - The generation script
- **src/utilities/searchUtils.ts** - Generated search index (auto-generated, do not edit)
- **src/types/search.ts** - TypeScript type definitions
- **src/components/SearchBar.vue** - Search UI component

## Future Enhancements

Potential improvements:
- Extract content from page template sections for more comprehensive indexing
- Add support for section-level search within pages
- Generate search index from markdown files
- Automatic regeneration during development (file watcher)
