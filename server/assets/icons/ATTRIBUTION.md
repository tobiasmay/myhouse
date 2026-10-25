# Curated app icons

Glasshouse Home reads an installed app's native icon by default (whatever
webOS ships for it, usually a small 80x80 or 130x130 PNG/JPEG/WebP). For a
short, hand-picked list of well-known streaming and media apps, this folder
holds a sharp vector icon instead, swapped in by `ICON_OVERRIDES` in
`home.html`. Everything else keeps its native icon; this is not an attempt
to replace or theme all app icons, just to avoid pixelation for the handful
of apps most people actually look at daily.

These SVGs are the same vetted sources the Luma launcher project
(ecklf/lg-luma) uses for its own curated artwork, reused here under the
same licenses it documents in its `assets.md`. Full original sources below;
none of this artwork was drawn by Glasshouse, and none of these brands are
affiliated with or endorse Glasshouse.

| File              | Source                                                                                 | License / attribution                   |
| ----------------- | --------------------------------------------------------------------------------------- | ---------------------------------------- |
| `netflix.svg`     | [Netflix](https://commons.wikimedia.org/wiki/File:Netflix_2015_logo.svg)                | Netflix Inc.; public-domain logo artwork |
| `youtube.svg`     | [YouTube](https://commons.wikimedia.org/wiki/File:YouTube_2024.svg)                     | Google Inc.; public-domain logo artwork  |
| `apple-tv.svg`    | [Apple TV](https://commons.wikimedia.org/wiki/File:Apple_TV_logo.svg)                    | Apple Inc.; public-domain logo artwork   |
| `disney-plus.svg` | [Disney+](https://commons.wikimedia.org/wiki/File:Disney%2B_logo.svg)                   | Disney Enterprises; public-domain logo artwork |
| `prime-video.svg` | [Prime Video](https://commons.wikimedia.org/wiki/File:Amazon_Prime_Video_logo.svg)       | Amazon; public-domain logo artwork       |
| `arte.svg`        | [ARTE](https://commons.wikimedia.org/wiki/File:Arte_Logo_2026.svg)                      | ARTE; public-domain logo artwork         |
| `das-erste.svg`   | [Das Erste](https://commons.wikimedia.org/wiki/File:Das_Erste_2014.svg)                 | ARD; public-domain logo artwork          |
| `zdf.svg`         | [ZDF](https://commons.wikimedia.org/wiki/File:ZDF_logo.svg)                             | ZDF; public-domain logo artwork          |
| `spotify.svg`     | [Spotify](https://commons.wikimedia.org/wiki/File:Spotify_logo_with_text.svg)           | Public-domain logo artwork               |
| `jellyfin.svg`    | [Jellyfin branding](https://github.com/jellyfin/jellyfin-ux/blob/master/branding/SVG/banner-dark.svg) | Jellyfin contributors; [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) (in-file attribution retained) |

Trademark and other underlying brand rights remain with the respective
owners; these marks are used only to identify the corresponding app.

Add another app to `ICON_OVERRIDES` by dropping a same-style SVG here and
pointing to its app ID (see the comment above `ICON_OVERRIDES` in
`home.html`) — no other code changes needed.
