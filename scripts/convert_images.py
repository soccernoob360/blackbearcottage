"""Convert every images/*.jpg to a same-named .webp (max 1600px long edge).
Runs in GitHub Actions via .github/workflows/convert-images.yml; skips files whose
.webp is already newer than the .jpg. Keeps the .jpg files (used for og:image)."""
import os
from PIL import Image

IMG_DIR = "images"
for f in sorted(os.listdir(IMG_DIR)):
    if not f.lower().endswith(".jpg"):
        continue
    src = os.path.join(IMG_DIR, f)
    out = os.path.join(IMG_DIR, f[:-4] + ".webp")
    if os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(src):
        continue
    im = Image.open(src).convert("RGB")
    w, h = im.size
    if max(w, h) > 1600:
        s = 1600 / max(w, h)
        im = im.resize((round(w * s), round(h * s)), Image.LANCZOS)
    q = 68 if os.path.getsize(src) > 200_000 else 76
    im.save(out, "WEBP", quality=q, method=6)
    print(f"{f}: {os.path.getsize(src)//1024} KB -> {os.path.getsize(out)//1024} KB ({im.size[0]}x{im.size[1]})")
