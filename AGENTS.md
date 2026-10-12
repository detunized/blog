# detunized.net

Hugo site. Netlify builds and deploys every push to `master`.

## Build and deploy

- The Hugo version is pinned in `netlify.toml`. Keep the local Hugo on the same version.
- Never put `published:` in post front matter, because Hugo reads it as a date and the build fails. `bin/medium.rb` adds it itself when cross-posting to dev.to.
- Netlify reports no status to GitHub. A deploy takes about a minute. Check it by curling the live page.
- Local preview: `hugo server --bind 127.0.0.1 --baseURL http://127.0.0.1:1313/ --renderToMemory`, plus `--buildDrafts` for drafts. With `localhost` the CSS doesn't load (IPv6). Without `--renderToMemory` the server writes into `public/`, so parallel servers overwrite each other.
- Before pushing, `HUGO_ENVIRONMENT=production hugo --gc --minify -d <temp dir>` should print no warnings. Google Analytics only renders in production.
- Games come from the Hugo module `github.com/detunized/lung-pong`, which is why Netlify needs `GO_VERSION`.

## Theme

- `themes/hermit` is a submodule on the fork `github.com/detunized/hermit`, which is patched for current Hugo.
- Push the theme through its `ssh` remote. `origin` is HTTPS and triggers keychain prompts.
- Push the theme before the site commit that bumps the submodule, or the Netlify build can't fetch it.
- Site styles go in `assets/scss/extra.scss`.
- Include the header with `partial`, not `partialCached`, because it highlights the current section.

## Photos

- Images are not in the repo. The master copy is `~/stuff/blog-photos/galleries/<folder>/`. It is served by the static Cloudflare Worker `detunized-photos` at `https://detunized-photos.detunized.workers.dev/galleries/<folder>/` (`params.imageHost`).
- `bin/deploy-photos.py` checks the master copy against the gallery pages and `data/photos.json`, then deploys it. Every deploy replaces all files, so only deploy from the complete master copy.
- Run wrangler only through that script. It runs wrangler from an empty directory, because in the blog directory wrangler detects Hugo and tries to deploy the whole site.
- The seedbox `dust.seedhost.eu` still has a copy of the galleries up to October 2026, so links to it from elsewhere keep working. Don't upload new galleries there.
- A gallery needs three things:
  - `content/photo/*.md` with `title`, `date` (published), `event_date` (sorts and groups the index), `folder` and `photos`.
  - Every image's size in `data/photos.json`.
  - A `title.jpg` banner in the folder.
- `bin/add-gallery.py` exports watermarked photos and the banner into the master copy and writes the page and the sizes. Run `bin/deploy-photos.py` before pushing the gallery commit.
- `content/photo/_content.gotmpl` generates a page for every photo at `/photo/<slug>/<n>/`.
  - It reads the gallery files from disk, so a running `hugo server` needs a restart after a gallery is added.
  - The pages are `build.list: never`, which keeps them out of counts, RSS and the sitemap.

## Style

- Keep the hermit look. Nothing that looks like a generic AI template. The accent color is `$soft-blue`, because the user didn't like the theme's teal on grey.
- Keep text short and plain. The About page covers work only, no family or hobbies. Don't use the word "freelance". The chosen wording is "Open to new projects".
- Posts should read like the existing ones. Write plain full sentences, often starting with "So," or "And", and casual numbers like "23 thousand". Avoid colon reveals, paired fragments and cute metaphors.
- Show visual changes on a local server before committing.
- Other agents may commit to this repo at the same time. Commit only your own files and `git pull --rebase` before pushing.
