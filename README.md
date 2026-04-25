# svg-tools — Glowforge Outline Generator

Upload any image and receive an SVG of just the outer silhouette, ready to send to a Glowforge laser cutter as a cut line.

## How it works

1. ML-based background removal isolates the subject — works on photos and clean line art
2. Only the outermost external contour is kept; all internal detail lines are discarded
3. `potrace` converts the solid silhouette to smooth Bézier curves
4. The SVG is styled with a red stroke and sized to 6″ on the longest edge

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

> **Note:** The first upload triggers a one-time download of the rembg background-removal model (~175 MB to `~/.u2net/`). Subsequent runs are fast.

## Run

```bash
python app.py
```

Open [http://127.0.0.1:5011](http://127.0.0.1:5011), upload an image, and download the outline SVG.

## Supported formats

JPEG · PNG · WEBP · BMP · TIFF · GIF (max 16 MB)

## Output SVG

| Property | Value | Notes |
|---|---|---|
| Stroke color | `#FF0000` | Glowforge auto-detects red as a cut operation |
| Fill | `none` | Vector cut line only, no fill |
| Stroke width | `12px` | Visible in preview; Glowforge cuts on path centerline |
| Document size | Longest edge = 6″ | Resize freely on the Glowforge bed |
| Curve style | Smooth Bézier via potrace | Clean curves, not polygonal segments |
