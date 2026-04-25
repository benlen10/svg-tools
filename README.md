# svg-tools — Glowforge Outline Generator

Upload any image and receive an SVG of just the outer silhouette, ready to send to a Glowforge laser cutter as a cut line.

## How it works

1. ML-based background removal isolates the subject (handles photos and line art)
2. Only the outermost external contour is kept — internal detail lines are discarded
3. `potrace` converts the silhouette to smooth Bézier curves
4. The SVG is styled with a red hairline stroke (Glowforge cut convention) at 6″ longest edge

## Prerequisites

**potrace** must be on your PATH:

```bash
brew install potrace
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> **Note:** The first run downloads the rembg background-removal model (~150 MB) to `~/.u2net/`. This is a one-time download.

## Run

```bash
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000), upload an image, and download the outline SVG.

## Output

- **Stroke:** `#FF0000` (red) — Glowforge auto-detects this as a cut operation
- **Fill:** none
- **Size:** longest edge defaults to 6″; resize freely on the Glowforge bed
- **Format:** SVG with smooth Bézier paths via potrace
