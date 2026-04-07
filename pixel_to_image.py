"""
pixel_to_image.py - Create PNG images from AI-generated 2D arrays of pixel data.

Supports multiple input formats so that an AI can produce pixel data in
whichever way is most natural:

  * Grayscale        – 2D array of ints (0-255)
  * Grayscale + Alpha – 2D array of [gray, alpha] pairs
  * RGB              – 2D array of [R, G, B] tuples/lists
  * RGBA             – 2D array of [R, G, B, A] tuples/lists
  * Hex strings      – 2D array of "#RRGGBB" or "#RRGGBBAA" strings
  * Named colors     – 2D array of CSS color names ("red", "transparent", …)
  * Palette-based    – 2D array of single-char (or short string) symbols
                       with a separate palette dict mapping symbols to colors

All values are clamped to [0, 255]. Rows that are shorter than the longest
row are right-padded with a configurable default color (transparent by default).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Sequence

from PIL import Image

# ── CSS named-color subset (full CSS Level 4 list) ──────────────────────────
# Keeping the most common ones; extend if needed.
_NAMED_COLORS: dict[str, tuple[int, int, int, int]] = {
    "transparent": (0, 0, 0, 0),
    "black": (0, 0, 0, 255),
    "white": (255, 255, 255, 255),
    "red": (255, 0, 0, 255),
    "green": (0, 128, 0, 255),
    "lime": (0, 255, 0, 255),
    "blue": (0, 0, 255, 255),
    "yellow": (255, 255, 0, 255),
    "cyan": (0, 255, 255, 255),
    "aqua": (0, 255, 255, 255),
    "magenta": (255, 0, 255, 255),
    "fuchsia": (255, 0, 255, 255),
    "silver": (192, 192, 192, 255),
    "gray": (128, 128, 128, 255),
    "grey": (128, 128, 128, 255),
    "maroon": (128, 0, 0, 255),
    "olive": (128, 128, 0, 255),
    "purple": (128, 0, 128, 255),
    "teal": (0, 128, 128, 255),
    "navy": (0, 0, 128, 255),
    "orange": (255, 165, 0, 255),
    "pink": (255, 192, 203, 255),
    "brown": (165, 42, 42, 255),
    "gold": (255, 215, 0, 255),
    "coral": (255, 127, 80, 255),
    "salmon": (250, 128, 114, 255),
    "khaki": (240, 230, 140, 255),
    "violet": (238, 130, 238, 255),
    "indigo": (75, 0, 130, 255),
    "turquoise": (64, 224, 208, 255),
    "tan": (210, 180, 140, 255),
    "skyblue": (135, 206, 235, 255),
    "tomato": (255, 99, 71, 255),
    "crimson": (220, 20, 60, 255),
    "lavender": (230, 230, 250, 255),
    "beige": (245, 245, 220, 255),
    "ivory": (255, 255, 240, 255),
    "mint": (189, 252, 201, 255),
    "peach": (255, 218, 185, 255),
}


def _clamp(v: int) -> int:
    """Clamp an integer to the 0-255 range."""
    return max(0, min(255, int(v)))


def _parse_hex(h: str) -> tuple[int, int, int, int]:
    """Parse a hex color string to (R, G, B, A)."""
    h = h.lstrip("#")
    if len(h) == 3:
        r, g, b = (int(c * 2, 16) for c in h)
        return (r, g, b, 255)
    if len(h) == 4:
        r, g, b, a = (int(c * 2, 16) for c in h)
        return (r, g, b, a)
    if len(h) == 6:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)
    if len(h) == 8:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(h[6:8], 16))
    raise ValueError(f"Invalid hex color: #{h}")


def _resolve_color(pixel: Any, palette: dict[str, Any] | None = None) -> tuple[int, int, int, int]:
    """
    Resolve a single pixel value to an (R, G, B, A) tuple.

    Accepted types:
      int            -> grayscale (alpha=255)
      [g, a]         -> grayscale + alpha
      [r, g, b]      -> RGB (alpha=255)
      [r, g, b, a]   -> RGBA
      str "#RRGGBB"  -> hex RGB
      str "#RRGGBBAA"-> hex RGBA
      str "red"      -> named color
      str symbol     -> looked up via palette dict
      None           -> transparent
    """
    if pixel is None:
        return (0, 0, 0, 0)

    # palette lookup first (symbol can be any string)
    if palette and isinstance(pixel, str) and pixel in palette:
        return _resolve_color(palette[pixel], palette=None)

    if isinstance(pixel, (int, float)):
        g = _clamp(int(pixel))
        return (g, g, g, 255)

    if isinstance(pixel, str):
        low = pixel.strip().lower()
        if low in _NAMED_COLORS:
            return _NAMED_COLORS[low]
        if low.startswith("#") or all(c in "0123456789abcdef" for c in low):
            return _parse_hex(pixel.strip())
        raise ValueError(f"Unknown color name or format: '{pixel}'")

    if isinstance(pixel, (list, tuple)):
        vals = [_clamp(int(v)) for v in pixel]
        if len(vals) == 1:
            return (vals[0], vals[0], vals[0], 255)
        if len(vals) == 2:
            return (vals[0], vals[0], vals[0], vals[1])
        if len(vals) == 3:
            return (vals[0], vals[1], vals[2], 255)
        if len(vals) == 4:
            return (vals[0], vals[1], vals[2], vals[3])
        raise ValueError(f"Pixel list must have 1-4 elements, got {len(vals)}")

    raise TypeError(f"Unsupported pixel type: {type(pixel)}")


def create_image(
    pixel_data: Sequence[Sequence[Any]],
    *,
    output_path: str | Path = "output.png",
    width: int | None = None,
    height: int | None = None,
    scale: int = 1,
    palette: dict[str, Any] | None = None,
    default_color: Any = None,
    background_color: Any = None,
) -> Path:
    """
    Create a PNG image from a 2D array of pixel data.

    Parameters
    ----------
    pixel_data : list[list[Any]]
        2D array where each element represents one pixel.
        See _resolve_color() for all accepted per-pixel formats.
        Rows may have different lengths; short rows are right-padded
        with *default_color*.

    output_path : str or Path
        Destination file path. Parent directories are created automatically.
        Defaults to "output.png".

    width : int, optional
        Target image width in pixels **before** scaling.
        If larger than the data, extra columns use *default_color*.
        If smaller, the data is cropped.
        Defaults to the length of the longest row.

    height : int, optional
        Target image height in pixels **before** scaling.
        If larger than the data, extra rows use *default_color*.
        If smaller, the data is cropped.
        Defaults to the number of rows.

    scale : int
        Integer upscale factor (nearest-neighbor). Each data pixel becomes
        a scale×scale block in the output. Useful for pixel art.
        Defaults to 1 (no scaling).

    palette : dict[str, Any], optional
        Mapping of symbol strings to color values. Enables a compact
        representation where each pixel is a short symbol (e.g. "R", "G", ".").
        Color values follow the same rules as individual pixels.

    default_color : Any
        Color used for padding / missing pixels. Defaults to transparent (None).

    background_color : Any
        If set, a background layer of this color is composited behind the image
        before saving. Useful for previewing transparent images.

    Returns
    -------
    Path
        The absolute path of the saved image.

    Examples
    --------
    Grayscale 3×3:
        create_image([[0, 128, 255], [64, 192, 32], [255, 0, 128]])

    RGB with transparency:
        create_image([
            [[255,0,0,128], [0,255,0,255]],
            [[0,0,255,255], [255,255,0,0]],
        ])

    Palette-based pixel art (scaled up 8×):
        create_image(
            [
                list("..RRRR.."),
                list(".RRRRRR."),
                list("RRRRRRRR"),
            ],
            palette={"R": "red", ".": "transparent"},
            scale=8,
        )

    Hex colors:
        create_image([["#ff0000", "#00ff00"], ["#0000ff", "#ffff00"]])
    """
    if not pixel_data or not any(pixel_data):
        raise ValueError("pixel_data must be a non-empty 2D array")

    # Determine dimensions from data
    data_height = len(pixel_data)
    data_width = max(len(row) for row in pixel_data)

    img_w = width if width is not None else data_width
    img_h = height if height is not None else data_height

    if img_w <= 0 or img_h <= 0:
        raise ValueError(f"Image dimensions must be positive, got {img_w}x{img_h}")

    if scale < 1:
        raise ValueError(f"Scale must be >= 1, got {scale}")

    default_rgba = _resolve_color(default_color, palette)

    # Build RGBA pixel buffer
    img = Image.new("RGBA", (img_w, img_h), default_rgba)

    for y in range(min(img_h, data_height)):
        row = pixel_data[y]
        for x in range(min(img_w, len(row))):
            rgba = _resolve_color(row[x], palette)
            img.putpixel((x, y), rgba)

    # Composite onto background if requested
    if background_color is not None:
        bg_rgba = _resolve_color(background_color, palette)
        bg = Image.new("RGBA", img.size, bg_rgba)
        img = Image.alpha_composite(bg, img)

    # Scale up (nearest-neighbor for pixel art)
    if scale > 1:
        img = img.resize((img_w * scale, img_h * scale), Image.NEAREST)

    # Ensure output directory exists
    out = Path(output_path).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    img.save(str(out), "PNG")
    return out


def create_image_from_json(
    json_path: str | Path,
    *,
    output_path: str | Path | None = None,
    **overrides: Any,
) -> Path:
    """
    Create an image from a JSON file containing pixel data and options.

    The JSON file should have the structure:
    {
        "pixel_data": [[...]],
        "output_path": "out.png",  (optional)
        "width": 16,               (optional)
        "height": 16,              (optional)
        "scale": 4,                (optional)
        "palette": {"R": "red"},   (optional)
        "default_color": null,     (optional)
        "background_color": null   (optional)
    }

    Any keyword argument passed to this function overrides the JSON value.
    """
    with open(json_path) as f:
        data = json.load(f)

    if not isinstance(data, dict) or "pixel_data" not in data:
        raise ValueError("JSON must be an object with a 'pixel_data' key")

    pixel_data = data.pop("pixel_data")
    # merge: JSON values as defaults, overrides take precedence
    kwargs = {**data, **{k: v for k, v in overrides.items() if v is not None}}
    if output_path is not None:
        kwargs["output_path"] = output_path

    return create_image(pixel_data, **kwargs)


def create_gradient(
    width: int,
    height: int,
    color_start: Any,
    color_end: Any,
    *,
    direction: str = "horizontal",
    output_path: str | Path = "gradient.png",
    scale: int = 1,
) -> Path:
    """
    Create a gradient image between two colors.

    Parameters
    ----------
    width, height : int
        Dimensions in pixels (before scaling).
    color_start, color_end : Any
        Start and end colors (any supported format).
    direction : str
        "horizontal", "vertical", or "diagonal".
    output_path, scale : see create_image.
    """
    c1 = _resolve_color(color_start)
    c2 = _resolve_color(color_end)

    pixels: list[list[tuple[int, ...]]] = []
    for y in range(height):
        row: list[tuple[int, ...]] = []
        for x in range(width):
            if direction == "horizontal":
                t = x / max(width - 1, 1)
            elif direction == "vertical":
                t = y / max(height - 1, 1)
            elif direction == "diagonal":
                t = (x + y) / max(width + height - 2, 1)
            else:
                raise ValueError(f"Unknown direction: {direction}")
            rgba = tuple(_clamp(int(c1[i] + (c2[i] - c1[i]) * t)) for i in range(4))
            row.append(rgba)
        pixels.append(row)

    return create_image(pixels, output_path=output_path, scale=scale)


def create_checkerboard(
    cols: int,
    rows: int,
    color_a: Any = "white",
    color_b: Any = "black",
    *,
    cell_size: int = 1,
    output_path: str | Path = "checkerboard.png",
    scale: int = 1,
) -> Path:
    """
    Create a checkerboard pattern.

    Parameters
    ----------
    cols, rows : int
        Number of cells horizontally and vertically.
    color_a, color_b : Any
        The two alternating colors.
    cell_size : int
        Size of each cell in pixels (before scaling).
    output_path, scale : see create_image.
    """
    pixels: list[list[Any]] = []
    for y in range(rows * cell_size):
        row: list[Any] = []
        for x in range(cols * cell_size):
            is_a = ((x // cell_size) + (y // cell_size)) % 2 == 0
            row.append(color_a if is_a else color_b)
        pixels.append(row)

    return create_image(pixels, output_path=output_path, scale=scale)


# ── CLI ──────────────────────────────────────────────────────────────────────

def main() -> None:
    """CLI entry point: read a JSON file and produce an image."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Create a PNG image from a JSON file of pixel data.",
    )
    parser.add_argument("json_file", help="Path to JSON file with pixel data")
    parser.add_argument("-o", "--output", help="Override output path")
    parser.add_argument("-s", "--scale", type=int, help="Override scale factor")
    parser.add_argument("--bg", help="Override background color")
    args = parser.parse_args()

    out = create_image_from_json(
        args.json_file,
        output_path=args.output,
        scale=args.scale,
        background_color=args.bg,
    )
    print(f"Image saved to {out}")


if __name__ == "__main__":
    main()
