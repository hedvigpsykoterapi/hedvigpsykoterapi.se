"""Regenerate website image variants from the original photos (Pillow + ImageMagick)."""
from pathlib import Path
import subprocess
from PIL import Image, ImageOps

root = Path(__file__).resolve().parents[1]
assets = root / 'assets'
assets.mkdir(exist_ok=True)

for name, original, widths in [
    ('hedvig-portrait', 'Hedvig bild hemsida.jpg', (420, 840, 1260)),
    ('coast', 'IMG_0548.JPG', (800, 1600, 2400)),
]:
    image = ImageOps.exif_transpose(Image.open(root / original)).convert('RGB')
    if name == 'coast':
        image = image.crop((0, 250, 3450, 2700))
    for width in widths:
        height = round(image.height * width / image.width)
        variant = image.resize((width, height), Image.Resampling.LANCZOS)
        stem = assets / f'{name}-{width}'
        variant.save(f'{stem}.webp', quality=78, method=6)
        variant.save(f'{stem}.jpg', quality=80, optimize=True, progressive=True)
        # Encode from a lossless intermediate, rather than the compressed JPEG.
        temporary = assets / f'.{name}-{width}.png'
        variant.save(temporary)
        subprocess.run(['magick', str(temporary), '-strip', '-quality', '48', f'{stem}.avif'], check=True)
        temporary.unlink()
        print(f'{name}: {width} × {height}')
