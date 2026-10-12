#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11"]
# ///
"""Export photos for a gallery (resized, watermarked) and register the gallery in the blog."""

import argparse
import datetime
import io
import json
import re
from pathlib import Path

from PIL import Image, ImageCms, ImageDraw, ImageFilter, ImageFont, ImageOps

BLOG = Path(__file__).resolve().parent.parent
PHOTOS_JSON = BLOG / "data/photos.json"
GALLERY_PAGES = BLOG / "content/photo"

# Twice the largest CSS size: the gallery column is 900px wide and photos are capped at 88vh in height
MAX_SIZE = (1800, 2400)
JPEG_QUALITY = 85
BANNER_SIZE = (1500, 300)

WATERMARK_TEXT = "© Dmitry Yakimenko (detunized.net)"
# Measured on the Lightroom exports at 900px: text 270px long, 7px from the right, 15px from the bottom
WATERMARK_LENGTH = 270 / 900
WATERMARK_RIGHT = 7 / 900
WATERMARK_BOTTOM = 15 / 900
WATERMARK_OPACITY = 0.85
SHADOW_OPACITY = 0.3
SHADOW_BLUR = 1.5 / 900
FONT_CANDIDATES = [
    Path.home() / "Library/Fonts/MyriadPro-Regular.otf",
    Path("/Library/Fonts/MyriadPro-Regular.otf"),
    Path("/System/Library/Fonts/Supplemental/PTSans.ttc"),
]

SRGB = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB"))


def to_srgb(image):
    image = ImageOps.exif_transpose(image)
    icc = image.info.get("icc_profile")
    if icc:
        source = ImageCms.ImageCmsProfile(io.BytesIO(icc))
        output_mode = "RGB" if image.mode in ("RGB", "CMYK", "L") else image.mode
        return ImageCms.profileToProfile(image, source, SRGB, outputMode=output_mode).convert("RGB")
    return image.convert("RGB")


def fit_within(image, size):
    scale = min(size[0] / image.width, size[1] / image.height)
    if scale >= 1:
        return image
    return image.resize((round(image.width * scale), round(image.height * scale)), Image.LANCZOS)


def watermark(image, font_path):
    long_side = max(image.size)
    font = ImageFont.truetype(font_path, 100)
    left, top, right, bottom = font.getbbox(WATERMARK_TEXT)
    font = font.font_variant(size=100 * WATERMARK_LENGTH * long_side / (right - left))
    left, top, right, bottom = font.getbbox(WATERMARK_TEXT)

    pad = round(4 * long_side / 900)
    mask = Image.new("L", (right - left + 2 * pad, bottom - top + 2 * pad))
    ImageDraw.Draw(mask).text((pad - left, pad - top), WATERMARK_TEXT, font=font, fill=255)
    mask = mask.rotate(90, expand=True)

    x = image.width - round(WATERMARK_RIGHT * long_side) - mask.width + pad
    y = image.height - round(WATERMARK_BOTTOM * long_side) - mask.height + pad
    shadow = mask.filter(ImageFilter.GaussianBlur(SHADOW_BLUR * long_side))

    result = image.convert("RGBA")
    for layer_mask, color, opacity in ((shadow, (0, 0, 0), SHADOW_OPACITY), (mask, (255, 255, 255), WATERMARK_OPACITY)):
        layer = Image.new("RGBA", mask.size, color + (0,))
        layer.putalpha(layer_mask.point(lambda v: round(v * opacity)))
        result.alpha_composite(layer, (x, y))
    return result.convert("RGB")


def banner(image, center):
    strip_height = image.width * BANNER_SIZE[1] / BANNER_SIZE[0]
    top = min(max(center * image.height - strip_height / 2, 0), image.height - strip_height)
    return image.resize(BANNER_SIZE, Image.LANCZOS, box=(0, top, image.width, top + strip_height))


def save_jpeg(image, path):
    image.save(path, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True, icc_profile=SRGB.tobytes())


def format_photos_json(data):
    lines = ["{"]
    for i, (folder, images) in enumerate(data.items()):
        lines.append(f'  "{folder}": {{')
        for j, (name, (width, height)) in enumerate(images.items()):
            lines.append(f'    "{name}": [{width}, {height}]' + ("," if j < len(images) - 1 else ""))
        lines.append("  }" + ("," if i < len(data) - 1 else ""))
    lines.append("}")
    return "\n".join(lines) + "\n"


def register_sizes(folder, sizes):
    data = json.loads(PHOTOS_JSON.read_text())
    data[folder] = sizes
    PHOTOS_JSON.write_text(format_photos_json(dict(sorted(data.items()))))


def write_page(title, date, event_date, folder, photos):
    existing = [p for p in GALLERY_PAGES.glob("*.md") if f"\nfolder: {folder}\n" in p.read_text()]
    if existing:
        page = existing[0]
        date = re.search(r"^date: (\S+)$", page.read_text(), re.M).group(1)
    else:
        page = GALLERY_PAGES / f"{date}-{re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')}.md"
    front = [f"title: {title}", f"date: {date}", f"event_date: '{event_date}'", f"folder: {folder}", "photos:"]
    page.write_text("---\n" + "\n".join(front + [f"- {p}" for p in photos]) + "\n---\n")
    return page


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title", required=True, help='for example "Santa Monica, June 2005"')
    parser.add_argument("--event-date", required=True, help="YYYY-MM-DD, used in the folder name and to group the index")
    parser.add_argument("--slug", required=True, help="short name used in the folder and file names")
    parser.add_argument("--images-dir", type=Path, default=Path.home() / "stuff/blog-photos/galleries",
                        help="the galleries/ folder that bin/deploy-photos.py deploys")
    parser.add_argument("--date", default=datetime.date.today().isoformat(), help="publication date, today by default")
    parser.add_argument("--banner", type=int, default=1, help="1-based number of the photo the banner is cut from")
    parser.add_argument("--banner-center", type=float, default=0.5, help="vertical center of the banner strip, 0 is the top")
    parser.add_argument("--font", type=Path, default=next((f for f in FONT_CANDIDATES if f.exists()), None))
    parser.add_argument("sources", nargs="+", type=Path, help="full resolution images in gallery order")
    args = parser.parse_args()

    folder = f"{args.event_date}-{args.slug}"
    out = args.images_dir / folder
    out.mkdir(parents=True, exist_ok=True)

    sizes, photos = {}, []
    for number, source in enumerate(args.sources, 1):
        name = f"{number:03d}-{args.slug}.jpg"
        image = to_srgb(Image.open(source))
        if number == args.banner:
            save_jpeg(banner(image, args.banner_center), out / "title.jpg")
        image = watermark(fit_within(image, MAX_SIZE), args.font)
        save_jpeg(image, out / name)
        sizes[name] = list(image.size)
        photos.append(name)
        print(f"{name} {image.width}x{image.height} <- {source}")

    sizes["title.jpg"] = list(BANNER_SIZE)
    register_sizes(folder, sizes)
    page = write_page(args.title, args.date, args.event_date, folder, photos)
    print(f"{out}\n{page.relative_to(BLOG)}")


if __name__ == "__main__":
    main()
