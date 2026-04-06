# Public Deploy

This project now supports a static public export.

## Build Locally

```bash
python3 /home/zhixin/code/study_system/scripts/build_public_site.py
```

Build output:

- `study_system/public/index.html`
- `study_system/public/tracking/index.html`

## Public Hosting Options

### GitHub Pages

This repo now includes a workflow:

- `.github/workflows/deploy-study-site.yml`

After pushing to GitHub:

1. Open repository settings
2. Open `Pages`
3. Set source to `GitHub Actions`

Official docs:

- https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site

### Cloudflare Pages

You can also point Cloudflare Pages at this repo and use:

- build command: `python3 study_system/scripts/build_public_site.py`
- output directory: `study_system/public`

Official docs:

- https://developers.cloudflare.com/pages/

## Notes

- The public site is fully static.
- Markdown content is rendered into HTML during export.
- `.nojekyll` is generated for GitHub Pages compatibility.
