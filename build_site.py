#!/usr/bin/env python3
"""
Build the SLEEP 2026 poster landing page (the QR target).

Generates, in this directory:
  - index.html              the landing page (references + contact + optional poster)
  - connor-baggot.vcf       vCard for the "Save to Contacts" button
  - qr.svg / qr.png         QR codes (vector + high-res raster) -> the live URL
  - qr-navy.svg             on-brand dark-indigo QR variant (optional)
  - .nojekyll              disables Jekyll on GitHub Pages
  - README.md              provenance / how-to-update

References are read LIVE from the canonical, hand-maintained file
"../Poster References.md" — edit that file and re-run to refresh the page.

The poster PDF is OPTIONAL: if a file named `poster.pdf` exists in this folder,
a "Download poster" button is included; otherwise that section is omitted. Drop
the final poster in as `poster.pdf` and re-run when the poster is done.

Run with the project venv so `segno` is importable:
    ../.qr_venv/bin/python build_site.py
"""

import glob
import html
import os
import re
import shutil

import segno

SITE_URL = "https://baggot4.github.io/sleep2026/"
HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
REF_FILE = os.path.join(os.path.dirname(HERE), "Poster References.md")

# ---------------------------------------------------------------- identity ----
NAME = "Connor Baggot"
EMAIL = "connor-baggot@uiowa.edu"
LINKEDIN = "https://www.linkedin.com/in/connor-baggot/"
AFFIL = "College of Liberal Arts & Sciences, University of Iowa"
ROLE = "Undergraduate Researcher"

TITLE = "Associations Between Dim Light Melatonin Onset and Salience Network Functional Connectivity in Later-Life Adults"

# NOTE: title / author / affiliation text mirrors the current poster
# (`DLMO_FC Poster SLEEP2026.pptx`, 2026-06-06). Update these strings if the poster changes.
AUTHORS_HTML = (
    '<strong>Connor Baggot</strong><sup>1</sup> &middot; '
    "Meina Zhang, PhD, RN<sup>2</sup> &middot; "
    "Karin Hoth, PhD<sup>3</sup> &middot; "
    "Navya Spurthi Thatikonda, MD, PhD<sup>3</sup> &middot; "
    "Eric Axelson, MS<sup>3</sup> &middot; "
    "Vincent Magnotta, PhD<sup>4</sup> &middot; "
    "Chooza Moon, PhD, RN<sup>2</sup>"
)
AFFILS_HTML = (
    "<sup>1</sup> College of Liberal Arts &amp; Sciences, University of Iowa &nbsp;&middot;&nbsp; "
    "<sup>2</sup> College of Nursing, University of Iowa &nbsp;&middot;&nbsp; "
    "<sup>3</sup> Carver College of Medicine, Department of Psychiatry, University of Iowa &nbsp;&middot;&nbsp; "
    "<sup>4</sup> Carver College of Medicine, Department of Radiology, University of Iowa"
)

TLDR = (
    "We measured the internal body clock of 50 cognitively healthy older adults "
    "(median age &asymp;68) using <strong>Dim Light Melatonin Onset (DLMO)</strong> &mdash; the "
    "gold-standard marker of circadian timing &mdash; and mapped resting-state functional "
    "connectivity with MRI. Adults with a <strong>later circadian rhythm</strong> (later DLMO) "
    "showed stronger connectivity specifically within the <strong>dorsal Salience Network "
    "(SN-B)</strong>, the system that shifts attention between inward and outward focus. The "
    "effect was <em>network-specific</em>: of 10 connections tested, only this one was "
    "significant &mdash; default-mode and hippocampal connections were unchanged. Because the "
    "salience network is among the networks affected early in Alzheimer&rsquo;s-related decline, "
    "circadian timing may be an early, network-specific signal of how the aging brain changes."
)

RESULT = (
    "Later DLMO &rarr; stronger within&ndash;Salience-Network-B connectivity &mdash; "
    "<strong>r = 0.37, p = 0.008</strong> "
    "(age/sex-adjusted r = 0.40, p = 0.004; FDR q = 0.04; n = 50)."
)

# Acknowledgments — verbatim from the current poster (`DLMO_FC Poster SLEEP2026.pptx`,
# 2026-06-06). NB the poster itself reads "NIH/ACTS"; the correct funder is NIH/NCATS
# (KL2TR002536 is an NCATS award) — mirrored as-is here per request.
FUNDING = (
    "The first author (Baggot) was supported by the University of Iowa Undergraduate Research "
    "Fellowship and University of Iowa Csomay Center (PI: Zhang). This work was supported by "
    "University of Iowa Csomay Center (PI: Moon), the University of Iowa Institute for Clinical "
    "and Translational Science (NIH/ACTS KL2TR002536, PI: Bassuk, Scholar: Moon), and the "
    "Alzheimer&rsquo;s Association (AARG-19-618403, PI: Moon). This work was conducted on an MRI "
    "instrument funded by 1S10OD025025-01. Contents are solely the responsibility of the authors "
    "and do not necessarily represent the official views of the University of Iowa, NIH/ACTS, or "
    "Alzheimer&rsquo;s Association."
)


# --------------------------------------------------------------- references ----
def load_references(path):
    """Parse the canonical 'Poster References.md' (numbered AMA lines).

    Each line looks like: '1. Authors. Title. *Journal.* 2020;1(2):3-4. doi:10.x/y'
    Returns a list of (html_text, href) where markdown *italics* -> <em> and the
    trailing 'doi:...' is split off into a clickable doi.org link.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Canonical reference file not found: {path}\n"
            "Expected 'Poster References.md' alongside the project."
        )
    refs = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            m = re.match(r"^\s*\d+\.\s+(.*\S)\s*$", line)
            if not m:
                continue
            raw = m.group(1)
            href = ""
            dm = re.search(r"\s*doi:\s*(\S+)\s*$", raw, re.I)
            if dm:
                href = "https://doi.org/" + dm.group(1)
                raw = raw[: dm.start()].rstrip()
            esc = html.escape(raw, quote=False)
            esc = re.sub(r"\*(.+?)\*", r"<em>\1</em>", esc)  # markdown italics
            refs.append((esc, href))
    return refs


def refs_html(refs):
    items = []
    for text, href in refs:
        link = ""
        if href:
            label = "doi.org/" + href.split("doi.org/", 1)[1]
            link = (
                f' <a class="doi" href="{html.escape(href)}" target="_blank" '
                f'rel="noopener">{html.escape(label)}</a>'
            )
        items.append(f"      <li>{text}{link}</li>")
    return "\n".join(items)


# ----------------------------------------------------------------- vCard ------
VCARD = (
    "BEGIN:VCARD\r\n"
    "VERSION:3.0\r\n"
    "N:Baggot;Connor;;;\r\n"
    "FN:Connor Baggot\r\n"
    "ORG:University of Iowa;College of Liberal Arts & Sciences\r\n"
    f"TITLE:{ROLE}\r\n"
    f"EMAIL;TYPE=INTERNET,PREF:{EMAIL}\r\n"
    f"URL;TYPE=LinkedIn:{LINKEDIN}\r\n"
    f"URL:{SITE_URL}\r\n"
    "NOTE:SLEEP 2026 (Baltimore) - DLMO & Salience Network Functional Connectivity in Later-Life Adults.\r\n"
    "END:VCARD\r\n"
)

# ------------------------------------------------------- poster section (opt) --
POSTER_SECTION = """    <section class="card">
      <div class="eyebrow">Poster</div>
      <h2>Download the full poster</h2>
      <p class="muted">The complete poster (figures, methods, and results table) as a PDF.</p>
      <div class="btns">
        <a class="btn btn-primary" href="poster.pdf" download>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          Poster PDF
        </a>
      </div>
    </section>
"""

# ------------------------------------------------------------- HTML template --
# Self-contained: inline CSS, system fonts (no network fonts), responsive,
# dusk/circadian theme. Tokens in {{...}} are replaced in main().
PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Connor Baggot &middot; DLMO &amp; Functional Connectivity &middot; SLEEP 2026</title>
<meta name="description" content="Poster references and contact for Dim Light Melatonin Onset (DLMO) and resting-state functional connectivity in later-life adults. SLEEP 2026, Connor Baggot, University of Iowa.">
<meta name="theme-color" content="#0f1430">
<meta property="og:title" content="Associations Between DLMO and Salience Network Functional Connectivity in Later-Life Adults">
<meta property="og:description" content="SLEEP 2026 poster &mdash; references and contact. Connor Baggot, University of Iowa.">
<meta property="og:type" content="website">
<meta property="og:url" content="{{SITE_URL}}">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%230f1430'/%3E%3Cpath d='M21 21.5A8 8 0 1 1 16.5 7a6.5 6.5 0 0 0 4.5 14.5z' fill='%23f3b53f'/%3E%3C/svg%3E">
<style>
  :root{
    --night:#0f1430; --night2:#222a63; --amber:#f3b53f; --amber-deep:#d8932a;
    --ink:#191c28; --muted:#5d6276; --surface:#ffffff; --bg:#eef0f6;
    --line:#e4e6ef; --link:#2740c8; --teal:#1f9d8f;
  }
  *{box-sizing:border-box}
  html{-webkit-text-size-adjust:100%}
  body{
    margin:0; background:var(--bg); color:var(--ink);
    font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    -webkit-font-smoothing:antialiased;
  }
  a{color:var(--link)}
  .wrap{max-width:780px; margin:0 auto; padding:0 18px}

  /* ---- hero ---- */
  .hero{
    position:relative; overflow:hidden; color:#f4f5fb;
    background:
      radial-gradient(120% 90% at 88% -10%, rgba(243,181,63,.30), transparent 55%),
      radial-gradient(90% 70% at 0% 0%, rgba(31,157,143,.18), transparent 50%),
      linear-gradient(165deg, #0c1029 0%, #141a45 55%, #1e2660 100%);
  }
  .hero .wrap{padding:40px 18px 34px}
  .badge{
    display:inline-flex; align-items:center; gap:8px; font-size:12.5px; letter-spacing:.06em;
    text-transform:uppercase; font-weight:600; color:#0f1430; background:var(--amber);
    padding:6px 12px; border-radius:999px;
  }
  .badge .dot{width:7px;height:7px;border-radius:50%;background:#0f1430}
  h1{
    font-family:Georgia,"Iowan Old Style","Times New Roman",serif;
    font-weight:600; font-size:clamp(25px,5.4vw,38px); line-height:1.18;
    margin:18px 0 14px; letter-spacing:.1px;
  }
  .authors{font-size:15px; color:#d9ddf2; margin:0 0 6px}
  .authors sup{color:var(--amber); font-weight:700}
  .affils{font-size:12.5px; color:#9aa2c8; margin:8px 0 0}
  .affils sup{color:var(--amber)}

  /* ---- cards ---- */
  main{padding:26px 0 10px}
  .card{
    background:var(--surface); border:1px solid var(--line); border-radius:16px;
    padding:22px 22px; margin:0 0 18px; box-shadow:0 1px 2px rgba(16,20,48,.04),0 8px 24px rgba(16,20,48,.05);
  }
  .eyebrow{
    display:flex; align-items:center; gap:9px; font-size:12px; font-weight:700; letter-spacing:.09em;
    text-transform:uppercase; color:var(--amber-deep); margin:0 0 12px;
  }
  .eyebrow::before{content:""; width:18px; height:3px; border-radius:2px; background:var(--amber)}
  h2{font-size:19px; margin:0 0 10px; font-weight:700}
  p{margin:0 0 12px}
  .lead{font-size:16.5px}
  .muted{color:var(--muted)}

  .result{
    margin-top:14px; padding:14px 16px; border-radius:12px; line-height:1.5;
    background:linear-gradient(180deg,#fff8e8,#fdf0d3); border:1px solid #f1dca0; color:#5a4410;
  }
  .result strong{color:#3f2f06}

  /* ---- contact buttons ---- */
  .btns{display:flex; flex-wrap:wrap; gap:10px; margin-top:6px}
  .btn{
    display:inline-flex; align-items:center; gap:9px; text-decoration:none; font-weight:600;
    font-size:15px; padding:12px 16px; border-radius:11px; border:1px solid transparent; cursor:pointer;
  }
  .btn svg{width:18px;height:18px;flex:none}
  .btn-primary{background:var(--amber); color:#241a02; border-color:var(--amber-deep)}
  .btn-primary:hover{background:#f5bf57}
  .btn-dark{background:var(--night); color:#fff}
  .btn-dark:hover{background:#1a2150}
  .btn-out{background:#fff; color:var(--ink); border-color:var(--line)}
  .btn-out:hover{border-color:#c9cde0; background:#fafbff}
  .contact-meta{margin:2px 0 16px; font-size:14.5px}
  .contact-meta .who{font-weight:700; font-size:16px}
  .tag{display:inline-block; font-size:11.5px; font-weight:700; letter-spacing:.04em; text-transform:uppercase;
       color:var(--teal); background:#e7f7f4; border:1px solid #c5ebe4; padding:2px 8px; border-radius:999px; margin-left:6px}

  /* ---- references ---- */
  ol.refs{margin:0; padding:0; counter-reset:r; list-style:none}
  ol.refs li{
    counter-increment:r; position:relative; padding:11px 0 11px 34px; border-bottom:1px solid var(--line);
    font-size:13.7px; line-height:1.5; color:#33384a;
  }
  ol.refs li:last-child{border-bottom:0}
  ol.refs li::before{
    content:counter(r); position:absolute; left:0; top:11px; width:24px; text-align:right;
    font-weight:700; color:var(--amber-deep); font-variant-numeric:tabular-nums;
  }
  a.doi{display:inline-block; margin-left:4px; color:var(--link); text-decoration:none; word-break:break-all; font-weight:600}
  a.doi:hover{text-decoration:underline}

  .funding{font-size:13px; color:var(--muted); line-height:1.6}

  footer{padding:8px 0 40px; text-align:center; color:var(--muted); font-size:12.5px}
  footer .affils{color:var(--muted); margin-bottom:8px}
  footer .affils sup{color:var(--amber-deep)}

  @media (max-width:480px){
    .card{padding:18px 16px; border-radius:14px}
    .btn{flex:1 1 100%; justify-content:center}
  }
</style>
</head>
<body>

  <header class="hero">
    <div class="wrap">
      <span class="badge"><span class="dot"></span>SLEEP 2026 &middot; Baltimore</span>
      <h1>{{TITLE}}</h1>
      <p class="authors">{{AUTHORS}}</p>
      <p class="affils">{{AFFILS}}</p>
    </div>
  </header>

  <main class="wrap">

    <section class="card" id="contact">
      <div class="eyebrow">Contact</div>
      <p class="contact-meta">
        <span class="who">{{NAME}}</span><span class="tag">Presenting author</span><br>
        <span class="muted">{{AFFIL}}</span>
      </p>
      <div class="btns">
        <a class="btn btn-primary" href="connor-baggot.vcf" download>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><line x1="19" y1="8" x2="19" y2="14"/><line x1="22" y1="11" x2="16" y2="11"/></svg>
          Save to Contacts
        </a>
        <a class="btn btn-dark" href="mailto:{{EMAIL}}?subject=SLEEP%202026%20poster%20%E2%80%94%20DLMO%20%26%20functional%20connectivity">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/></svg>
          Email me
        </a>
        <a class="btn btn-out" href="{{LINKEDIN}}" target="_blank" rel="noopener">
          <svg viewBox="0 0 24 24" fill="currentColor"><path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2zM8.34 18.34V10.4H5.67v7.94zM7 9.24a1.55 1.55 0 1 0 0-3.1 1.55 1.55 0 0 0 0 3.1m11.34 9.1v-4.36c0-2.33-1.25-3.41-2.91-3.41a2.51 2.51 0 0 0-2.28 1.25v-1.42h-2.67v7.94h2.67v-4.39c0-1.16.22-2.28 1.65-2.28s1.42 1.32 1.42 2.35v4.32z"/></svg>
          LinkedIn
        </a>
      </div>
    </section>

{{POSTER_SECTION}}
    <section class="card">
      <div class="eyebrow">References</div>
      <h2>Full reference list</h2>
      <ol class="refs">
{{REFERENCES}}
      </ol>
    </section>

    <section class="card">
      <div class="eyebrow">Acknowledgments</div>
      <p class="funding">{{FUNDING}}</p>
    </section>

  </main>

  <footer class="wrap">
    <p class="affils">{{AFFILS}}</p>
    <p>Presented at SLEEP 2026, the 40th annual meeting of the Associated Professional Sleep Societies.</p>
  </footer>

</body>
</html>
"""


def main():
    refs = load_references(REF_FILE)

    # Optional poster: include the download section only if poster.pdf is present.
    # (Drop the final poster in as poster.pdf and re-run to add it.)
    pdf_renamed = False
    if not os.path.exists("poster.pdf"):
        cands = [p for p in glob.glob("*.pdf") if p != "poster.pdf"]
        if cands:
            shutil.move(cands[0], "poster.pdf")
            pdf_renamed = True
    has_poster = os.path.exists("poster.pdf")
    poster_block = (POSTER_SECTION + "\n") if has_poster else ""

    page = PAGE
    repl = {
        "{{SITE_URL}}": SITE_URL,
        "{{TITLE}}": TITLE,
        "{{AUTHORS}}": AUTHORS_HTML,
        "{{AFFILS}}": AFFILS_HTML,
        "{{TLDR}}": TLDR,
        "{{RESULT}}": RESULT,
        "{{NAME}}": NAME,
        "{{AFFIL}}": AFFIL,
        "{{EMAIL}}": EMAIL,
        "{{LINKEDIN}}": LINKEDIN,
        "{{FUNDING}}": FUNDING,
        "{{POSTER_SECTION}}": poster_block,
        "{{REFERENCES}}": refs_html(refs),
    }
    for k, v in repl.items():
        page = page.replace(k, v)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(page)

    with open("connor-baggot.vcf", "w", encoding="utf-8", newline="") as f:
        f.write(VCARD)

    with open(".nojekyll", "w") as f:
        f.write("")

    # QR codes -> the live URL. error='m' (15%) keeps the symbol low-density so it
    # scans easily from poster-viewing distance; border=4 = required quiet zone.
    qr = segno.make(SITE_URL, error="m")
    qr.save("qr.svg", scale=12, border=4, dark="#000000", light="#ffffff")
    qr.save("qr.png", scale=40, border=4, dark="#000000", light="#ffffff")
    qr.save("qr-navy.svg", scale=12, border=4, dark="#0f1430", light="#ffffff")
    ver = qr.version
    modules = 17 + 4 * ver

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(
            "# SLEEP 2026 poster — references & contact\n\n"
            f"Landing page for the QR code on Connor Baggot's SLEEP 2026 poster, "
            f"*{TITLE}*. Live at <{SITE_URL}>.\n\n"
            "The QR code (`qr.svg` / `qr.png`) encodes that URL and never changes, so it can "
            "go on the poster now while the page content is still being finalized.\n\n"
            "## Update the page\n\n"
            "1. **References** — edit `../Poster References.md` (the canonical list).\n"
            "2. **Authors / affiliations / acknowledgments** — edit the constants near the top "
            "of `build_site.py`.\n"
            "3. **Add the poster PDF** — drop the finished poster in here as `poster.pdf` "
            "(a Download button appears automatically).\n"
            "4. **Rebuild**, then commit & push:\n\n"
            "```bash\n"
            "../.qr_venv/bin/python build_site.py\n"
            "git add -A && git commit -m \"update\" && git push\n"
            "```\n"
        )

    print(f"QR URL        : {SITE_URL}")
    print(f"QR version    : {ver}  ({modules}x{modules} modules + quiet zone)")
    print(f"References     : {len(refs)}  (from {os.path.basename(REF_FILE)})")
    print(f"Poster section : {'included (poster.pdf present)' if has_poster else 'omitted (no poster.pdf yet)'}")
    print(f"PDF renamed    : {pdf_renamed}")
    print("Dir contents   : " + ", ".join(sorted(os.listdir("."))))


if __name__ == "__main__":
    main()
