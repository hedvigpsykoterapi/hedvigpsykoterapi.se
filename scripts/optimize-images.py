"""Regenerate website image variants from the original photos (Pillow + ImageMagick)."""
from pathlib import Path
import subprocess
from PIL import Image, ImageOps

root = Path(__file__).resolve().parents[1]
assets = root / 'assets'
assets.mkdir(exist_ok=True)

import argparse

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--only", help="Regenerate only the named image asset")
args = parser.parse_args()

for name, original, widths in [
    ('lake-sun', 'sjöisol.jpg', (480, 800, 1200)),
    ('room', 'rummet.jpg', (480, 800, 1200, 1600)),
    ('hedvig-portrait', 'Hedvig bild hemsida.jpg', (420, 840)),
    ('coast', 'IMG_0548.JPG', (800, 1600, 2400)),
    ('beach-footprints-clean', 'assets/beach-footprints-clean.png', (240, 280, 480, 560, 840)),
]:
    if args.only and name != args.only:
        continue
    image = ImageOps.exif_transpose(Image.open(root / original)).convert('RGB')
    if name == 'coast':
        image = image.crop((0, 250, 3450, 2700))
    for width in widths:
        height = round(image.height * width / image.width)
        # Bicubic reduces harsh sand texture; size variants avoid excessive browser scaling.
        resampling = Image.Resampling.BICUBIC if name == 'beach-footprints-clean' else Image.Resampling.LANCZOS
        variant = image.resize((width, height), resampling)
        stem = assets / f'{name}-{width}'
        variant.save(f'{stem}.webp', quality=78, method=6)
        variant.save(f'{stem}.jpg', quality=80, optimize=True, progressive=True)
        # Encode from a lossless intermediate, rather than the compressed JPEG.
        temporary = assets / f'.{name}-{width}.png'
        variant.save(temporary)
        subprocess.run(['magick', str(temporary), '-strip', '-quality', '48', f'{stem}.avif'], check=True)
        temporary.unlink()
        print(f'{name}: {width} × {height}')
