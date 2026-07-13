# Safe publishing workflow

This repository is the deployment source for `https://www.graywoods.me`. Obsidian drafts remain outside this repository until Hoik explicitly asks to publish one.

## Safety contract

- Authoring source: `/opt/data/graywoods/4. Matter/posts/`
- Published posts: `src/content/posts/`
- Hero images: `public/images/`
- Approval signal: an explicit instruction such as `이 글 게시해줘`
- Never push a draft directly to `main`.
- Never use `git add .` or `git add -A` for a content publication.
- Never overwrite or delete an existing post or image through the preparation script.
- Never commit `dist/` or `.astro/` changes as part of a post publication.
- Never place GitHub or Vercel credentials in this repository, the Obsidian vault, or chat.

## Hero image contract

- JPEG
- exactly 1200 x 630 pixels
- no text embedded in the image unless explicitly requested
- focal subject kept in the central safe area for card and article-header crops
- filename generated as `YYYY-MM-DD-slug.jpg`

## Prepare one approved post

Dry-run is the default:

```bash
python3 scripts/prepare-post.py \
  '/opt/data/graywoods/4. Matter/posts/ARTICLE.md' \
  --slug 'stable-url-slug' \
  --date YYYY-MM-DD \
  --image '/absolute/path/to/1200x630.jpg'
```

Review the listed source and destinations. Only then repeat with `--apply`:

```bash
python3 scripts/prepare-post.py \
  '/opt/data/graywoods/4. Matter/posts/ARTICLE.md' \
  --slug 'stable-url-slug' \
  --date YYYY-MM-DD \
  --image '/absolute/path/to/1200x630.jpg' \
  --apply
```

The script:

1. accepts sources only from the verified Obsidian posts folder;
2. requires the source to remain `draft: true`;
3. rejects unresolved Obsidian wikilinks, embeds, and local image paths;
4. validates a 1200 x 630 JPEG hero image;
5. creates a separate published copy with `draft: false`;
6. refuses all destination collisions;
7. runs `npm run verify` and rolls back newly created files on failure;
8. never stages, commits, pushes, merges, or deploys.

Use `--without-image` only as an explicit exception.

## Review and publish

Start from a clean branch based on the latest remote `main`:

```bash
git fetch origin main
git switch -c publish/YYYY-MM-DD-slug origin/main
```

After preparation, stage only the intended post and image by exact path:

```bash
git add -- 'src/content/posts/YYYY-MM-DD-slug.md' 'public/images/YYYY-MM-DD-slug.jpg'
git diff --cached --name-status
git diff --cached --stat
npm run check:protected-content -- origin/main
```

The staged diff must contain no deletion (`D`), no generated build output, and no unrelated file. Run the safety test again before committing:

```bash
npm run verify
```

Push the publication branch and open a pull request. GitHub Actions rejects changes, deletions, or renames of historical posts and images; a publication pull request may add new content only. Confirm that check and the Vercel Preview before merging. After merge, verify the production page, image, tags, RSS inclusion, and final URL.

## Draft protection

`npm run verify` creates a uniquely named temporary draft with exclusive file creation, builds the complete site, and fails if the sentinel appears in any route, tag, RSS, sitemap, or search output. It removes only the fixture created by that invocation, even when the test fails.

Draft visibility is controlled centrally by `src/utils/posts.js` and applied to:

- homepage
- direct post routes
- tag index and tag pages
- RSS
- 404 recent-post links
- sitemap and Pagefind indirectly, because no draft route is generated

## Deliberately separate work

The repository currently tracks historical `dist/` and `.astro/` output. Cleaning those files and updating vulnerable dependencies must be done in separate reviewed branches. Do not mix either task into a post publication.
