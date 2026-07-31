# Presentation assets

`lulucf-frf-demo-qr.png` — QR code encoding this repository's own URL
(`https://github.com/ctrees-products/lulucf-frf-demo`), for slides and printed
handouts. 41×41 modules, error-correction level M, 820×820 px with the
spec-minimum 4-module quiet zone.

It decodes reliably down to about 120 px, so keep it at roughly half an inch or
larger on a slide and don't crop the white border — the quiet zone is part of the
code, not padding. Regenerate with `segno.make(URL, error='m')` if the URL ever
changes.
