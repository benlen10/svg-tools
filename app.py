from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, Response, url_for

from outline import image_to_outline_svg

app = Flask(__name__)
app.secret_key = "glowforge-outline-secret"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {
    "jpg", "jpeg", "png", "webp", "bmp", "tiff", "tif", "gif",
}


def _allowed(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/convert", methods=["POST"])
def convert():
    file = request.files.get("image")
    if not file or file.filename == "":
        flash("Please select an image file.")
        return redirect(url_for("index"))

    if not _allowed(file.filename):
        flash(f"Unsupported file type. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}")
        return redirect(url_for("index"))

    try:
        svg_bytes = image_to_outline_svg(file.read())
    except FileNotFoundError:
        flash("potrace is not installed. Run: brew install potrace")
        return redirect(url_for("index"))
    except Exception as exc:
        flash(f"Conversion failed: {exc}")
        return redirect(url_for("index"))

    stem = Path(file.filename).stem
    return Response(
        svg_bytes,
        mimetype="image/svg+xml",
        headers={"Content-Disposition": f'attachment; filename="{stem}-outline.svg"'},
    )


if __name__ == "__main__":
    app.run(debug=True, port=5011)
