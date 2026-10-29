# Profile setup

This repository is the source of the GitHub profile at
[github.com/thiagoyb11](https://github.com/thiagoyb11).

## Publish the profile

Keep this repository public and named `thiagoyb11`. GitHub displays the root
`README.md` on the profile automatically.

From this directory, review local changes and publish them when ready:

```sh
git diff
git status --short
git add README.md assets scripts docs/setup.md
git commit -m "feat: add animated ASCII profile header"
git push origin main
```

The remote is already configured as
`https://github.com/thiagoyb11/thiagoyb11.git`.

## Suggested profile bio

Paste this into the **Bio** field under **Edit profile** on GitHub:

> Information Systems Engineering student at UTN Santa Fe. Building applications with React, TypeScript and Spring Boot. Interested in algorithms and C++.

The profile bio is separate from the repository README.

## Edit the profile

- Update `README.md` to change the introduction, technologies, or contact link.
- Edit `scripts/render_header.py` to change the ASCII lettering, animation, or colors.
- The header follows the visitor's preferred color scheme, with a light fallback.
- Visitors who prefer reduced motion see a static PNG instead of the GIF.
- The artwork is stored in this repository. It uses no external images or widgets.

No installation, build step, API tokens, or GitHub Actions are required to display the profile.

## Regenerate the animation

Only the optional generator needs Python 3.10+ and Pillow:

```sh
python3 -m pip install Pillow
python3 scripts/render_header.py
```

The script produces the light and dark GIFs and their static PNG fallbacks. Each
GIF loops continuously for 5.76 seconds at 1400 by 420 pixels. All visible artwork
uses ASCII characters, rendered with a local monospace font. Menlo, DejaVu Sans
Mono, and Consolas are detected automatically; use `--font /path/to/font.ttf`
when needed.

Reference: [GitHub profile README documentation](https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme).
