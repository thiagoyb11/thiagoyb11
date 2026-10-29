"""Generate the profile's ASCII GIF banners. Requires Pillow (pip install pillow)."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH, HEIGHT = 1400, 420
FRAMES, DURATION = 96, 60
COLS, ROWS = 72, 36
RAMP = ".,:;irsXA253hMHGS#9B&@"
LETTERING = [
    "##### #   # #####  ###   ####  ### ",
    "  #   #   #   #   #   # #     #   #",
    "  #   #   #   #   #   # #     #   #",
    "  #   #####   #   ##### # ### #   #",
    "  #   #   #   #   #   # #   # #   #",
    "  #   #   #   #   #   # #   # #   #",
    "  #   #   # ##### #   #  ###   ### ",
]


def load_font(size: int, override: str | None) -> ImageFont.FreeTypeFont:
    candidates = [
        override,
        "/System/Library/Fonts/Menlo.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "C:/Windows/Fonts/consola.ttf",
        "DejaVuSansMono.ttf",
    ]
    for candidate in candidates:
        if candidate:
            try:
                return ImageFont.truetype(candidate, size)
            except OSError:
                pass
    raise SystemExit("Monospace font not found. Pass --font /path/to/font.ttf.")


def surface() -> list[tuple[float, ...]]:
    points = []
    for i in range(150):
        theta = math.tau * i / 150
        ct, st = math.cos(theta), math.sin(theta)
        for j in range(64):
            phi = math.tau * j / 64
            cp, sp = math.cos(phi), math.sin(phi)
            radius = 2.05 + 0.8 * cp
            points.append((radius * ct, radius * st, 0.8 * sp, cp * ct, cp * st, sp))
    return points


def ascii_frame(points: list[tuple[float, ...]], phase: float) -> list[str]:
    ca, sa = math.cos(phase + 0.65), math.sin(phase + 0.65)
    cb, sb = math.cos(phase + 0.3), math.sin(phase + 0.3)
    depth = [float("inf")] * (COLS * ROWS)
    cells = [" "] * (COLS * ROWS)
    for x, y, z, nx, ny, nz in points:
        # Rotate both the surface and its normals around two axes.
        yy, zz = y * ca - z * sa, y * sa + z * ca
        xx, yy = x * cb - yy * sb, x * sb + yy * cb
        nny, nnz = ny * ca - nz * sa, ny * sa + nz * ca
        nnx, nny = nx * cb - nny * sb, nx * sb + nny * cb
        distance = zz + 9.5
        col = round(COLS / 2 + 66 * xx / distance)
        row = round(ROWS / 2 - 48 * yy / distance)
        if not (0 <= col < COLS and 0 <= row < ROWS):
            continue
        index = row * COLS + col
        if distance < depth[index]:
            light = max(0, -0.3 * nnx + 0.45 * nny - 0.84 * nnz)
            shade = min(len(RAMP) - 1, int((0.08 + 0.92 * light) * (len(RAMP) - 1)))
            depth[index] = distance
            cells[index] = RAMP[shade]
    return ["".join(cells[row * COLS:(row + 1) * COLS]) for row in range(ROWS)]


def mix(a: tuple[int, ...], b: tuple[int, ...], amount: float) -> tuple[int, ...]:
    return tuple(round(x + (y - x) * amount) for x, y in zip(a, b))


def render(output: Path, font_path: str | None) -> None:
    output.mkdir(parents=True, exist_ok=True)
    font = load_font(12, font_path)
    title = load_font(25, font_path)
    small = load_font(15, font_path)
    label = load_font(14, font_path)
    mesh = surface()
    ascii_frames = [ascii_frame(mesh, math.tau * i / FRAMES) for i in range(FRAMES)]

    for theme, bg, fg in [
        ("dark", (13, 17, 23), (211, 224, 238)),
        ("light", (246, 248, 250), (48, 64, 83)),
    ]:
        palette = Image.new("P", (1, 1))
        colors = [v for i in range(256) for v in mix(bg, fg, i / 255)]
        palette.putpalette(colors)
        base = Image.new("RGB", (WIDTH, HEIGHT), bg)
        draw = ImageDraw.Draw(base)
        draw.rounded_rectangle((0, 0, WIDTH - 1, HEIGHT - 1), radius=16,
                               outline=mix(bg, fg, 0.2), width=2)
        draw.text((52, 31), "thiagoyb11@github:~$ whoami", font=small,
                  fill=mix(bg, fg, 0.65))
        draw.line((52, 72, WIDTH - 52, 72), fill=mix(bg, fg, 0.13))
        for row, text in enumerate(LETTERING):
            draw.text((52, 102 + row * 24), text, font=title, fill=mix(bg, fg, 0.96))
        draw.text((54, 297), "Y O R I S  B E R T S C H I", font=label,
                  fill=mix(bg, fg, 0.7))
        draw.text((54, 343), "Information Systems Engineering", font=small,
                  fill=mix(bg, fg, 0.72))
        draw.text((54, 369), "UTN Santa Fe / Argentina", font=label,
                  fill=mix(bg, fg, 0.51))
        frames = []
        for lines in ascii_frames:
            frame = base.copy()
            ink = ImageDraw.Draw(frame)
            for row, line in enumerate(lines):
                ink.text((800, 52 + row * 10), line, font=font, fill=mix(bg, fg, 0.84))
            frames.append(frame.quantize(palette=palette, dither=Image.Dither.NONE))
        target = output / f"header-ascii-{theme}.gif"
        frames[0].save(target, save_all=True, append_images=frames[1:], duration=DURATION,
                       loop=0, disposal=1, optimize=True)
        frames[0].convert("RGB").save(output / f"header-ascii-{theme}.png")
        print(f"{target.name}: {FRAMES} frames, {FRAMES * DURATION / 1000:.2f}s, "
              f"{target.stat().st_size / 1024:.0f} KiB")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font", help="Path to a monospace TTF/TTC font")
    parser.add_argument("--output", type=Path,
                        default=Path(__file__).resolve().parents[1] / "assets")
    args = parser.parse_args()
    render(args.output, args.font)
