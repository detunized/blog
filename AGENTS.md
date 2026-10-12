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

- Images are not in the repo. They live on a seedbox: `https://dust.seedhost.eu/detunized/detunized.net/galleries/<folder>/` (`params.imageHost`). The ssh host is `dust.seedhost.eu` and the directory is `www/detunized.dust.seedhost.eu/detunized/detunized.net/galleries/`. The old `raw.seedhost.eu` host is dead.
- A gallery needs three things:
  - `content/photo/*.md` with `title`, `date` (published), `event_date` (sorts and groups the index), `folder` and `photos`.
  - Every image's size in `data/photos.json`.
  - A `title.jpg` banner in the folder.
- `bin/add-gallery.py` exports watermarked photos and the banner to a local folder, then writes the page and the sizes. Upload with `rsync -a --chmod=D755,F644 <local>/<folder> dust.seedhost.eu:<directory above>`.
- `content/photo/_content.gotmpl` generates a page for every photo at `/photo/<slug>/<n>/`.
  - It reads the gallery files from disk, so a running `hugo server` needs a restart after a gallery is added.
  - The pages are `build.list: never`, which keeps them out of counts, RSS and the sitemap.

## Style

- Keep the hermit look. Nothing that looks like a generic AI template. The accent color is `$soft-blue`, because the user didn't like the theme's teal on grey.
- Keep text short and plain. The About page covers work only, no family or hobbies. Don't use the word "freelance". The chosen wording is "Open to new projects".
- Posts should read like the existing ones. Write plain full sentences, often starting with "So," or "And", and casual numbers like "23 thousand". Avoid colon reveals, paired fragments and cute metaphors.
- Show visual changes on a local server before committing.
- Other agents may commit to this repo at the same time. Commit only your own files and `git pull --rebase` before pushing.
