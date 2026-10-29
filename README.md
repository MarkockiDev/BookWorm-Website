# ilovebookworm.com

The BookWorm landing page. Plain HTML and CSS with a few lines of JavaScript: no build step, no dependencies.

```
index.html          the landing page
privacy/index.html  the privacy policy (copied from Website/index.html in the app repo)
404.html            shown by GitHub Pages for any missing page
CNAME               the custom domain, ilovebookworm.com
assets/             icons, worms, portrait, Open Graph image (og-image.jpg)
assets/shots/       App Store 4.0 screenshots cropped for the web, per theme (light, dark, retro, marginalia)
```

## Preview locally

```bash
python3 -m http.server 8765 --directory "NEW WEBSITE"
```

Then open http://localhost:8765.

## Publish on GitHub Pages

1. Create a new **public** repository (for example `bookworm-site`) and push the contents of this folder to the root of its `main` branch.
2. In the repository: **Settings → Pages → Build and deployment → Deploy from a branch → `main` / `(root)`**.
3. Under **Custom domain** enter `ilovebookworm.com` (the `CNAME` file already says so) and save.
4. At your domain registrar, add these DNS records:
   - `A` records for `ilovebookworm.com` → `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - `AAAA` records (optional, IPv6) → `2606:50c0:8000::153`, `2606:50c0:8001::153`, `2606:50c0:8002::153`, `2606:50c0:8003::153`
   - `CNAME` record for `www` → `<your-github-username>.github.io`
5. Wait for the DNS check to pass, then tick **Enforce HTTPS**.
6. Optional but recommended: verify the domain under your GitHub account (**Settings → Pages → Verified domains**) so nobody else can claim it.

## Afterwards

- The app's Privacy Policy link still points at `markockidev.github.io/BookWorm-Privacy-Policy`. Once this site is live, `https://ilovebookworm.com/privacy/` can replace it in the app and in App Store Connect.
- If the privacy policy changes, update both copies (or retire the old one) and the "Last updated" date.
- New screenshots: crop the phone from each App Store panel the same way (`magick in.png -crop 1126x1887+40+735 +repage -resize 720x -quality 80 out-720.webp`, and again at 420 wide).
