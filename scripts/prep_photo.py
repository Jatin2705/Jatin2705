from pathlib import Path
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove


def main():
    source = Path(sys.argv[1] if len(sys.argv) > 1 else "source-photo.jpg")
    output = Path("source-prepped.png")
    if not source.exists():
        raise SystemExit(f"Photo not found: {source}")

    rgba = remove(source.read_bytes())
    image = Image.open(__import__("io").BytesIO(rgba)).convert("RGBA")
    arr = np.array(image)

    rgb = arr[:, :, :3]
    alpha = arr[:, :, 3:4] / 255.0
    white = np.full_like(rgb, 255)
    composited = (rgb * alpha + white * (1 - alpha)).astype(np.uint8)

    gray = cv2.cvtColor(composited, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    gray = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)

    Image.fromarray(gray).save(output)
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
