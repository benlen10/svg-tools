import subprocess
import tempfile
import xml.etree.ElementTree as ET
from io import BytesIO
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove


def image_to_outline_svg(image_bytes: bytes, target_inches: float = 6.0) -> bytes:
    img = Image.open(BytesIO(image_bytes)).convert("RGBA")

    no_bg: Image.Image = remove(img)

    alpha = np.array(no_bg)[..., 3]
    mask = (alpha > 128).astype(np.uint8) * 255

    # Seal small perimeter gaps before contouring
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # Draw filled external contours only → solid silhouette (no internal lines)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    silhouette = np.zeros_like(mask)
    cv2.drawContours(silhouette, contours, -1, color=255, thickness=cv2.FILLED)

    h, w = silhouette.shape
    with tempfile.TemporaryDirectory() as tmp:
        pbm_path = Path(tmp) / "mask.pbm"
        svg_path = Path(tmp) / "outline.svg"

        # PBM: 1 = black (foreground for potrace), 0 = white (background)
        # potrace traces black pixels, so invert our white-on-black mask
        pbm_img = Image.fromarray(255 - silhouette)
        pbm_img.save(str(pbm_path))

        result = subprocess.run(
            ["potrace", "--svg", "--output", str(svg_path), str(pbm_path)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"potrace failed: {result.stderr.strip()}")

        raw_svg = svg_path.read_bytes()

    return _restyle_for_glowforge(raw_svg, w, h, target_inches)


def _restyle_for_glowforge(
    svg_bytes: bytes, px_w: int, px_h: int, target_inches: float
) -> bytes:
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    tree = ET.parse(BytesIO(svg_bytes))
    root = tree.getroot()
    ns = "http://www.w3.org/2000/svg"

    # Size the document in inches, longest edge = target_inches
    scale = target_inches / max(px_w, px_h)
    w_in = round(px_w * scale, 4)
    h_in = round(px_h * scale, 4)
    root.set("width", f"{w_in}in")
    root.set("height", f"{h_in}in")
    root.set("viewBox", f"0 0 {px_w} {px_h}")

    # potrace emits groups and paths with fill="black". Restyle everything for
    # a Glowforge cut line: red hairline stroke, no fill.
    for elem in root.iter(f"{{{ns}}}g"):
        elem.attrib.pop("fill", None)
        elem.attrib.pop("stroke", None)
    for elem in root.iter(f"{{{ns}}}path"):
        elem.set("fill", "none")
        elem.set("stroke", "#FF0000")
        elem.set("stroke-width", "12px")

    out = BytesIO()
    tree.write(out, encoding="utf-8", xml_declaration=True)
    return out.getvalue()
