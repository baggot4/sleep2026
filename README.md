# SLEEP 2026 poster — references & contact

Landing page for the QR code on Connor Baggot's SLEEP 2026 poster, *Associations Between Dim Light Melatonin Onset and Salience Network Functional Connectivity in Later-Life Adults*. Live at <https://baggot4.github.io/sleep2026/>.

The QR code (`qr.svg` / `qr.png`) encodes that URL and never changes, so it can go on the poster now while the page content is still being finalized.

## Update the page

1. **References** — edit `../Poster References.md` (the canonical list).
2. **Authors / affiliations / acknowledgments** — edit the constants near the top of `build_site.py`.
3. **Add the poster PDF** — drop the finished poster in here as `poster.pdf` (a Download button appears automatically).
4. **Rebuild**, then commit & push:

```bash
../.qr_venv/bin/python build_site.py
git add -A && git commit -m "update" && git push
```
