"""Generate the profile's ASCII GIF banners. Requires Pillow (pip install pillow)."""

from __future__ import annotations

import argparse
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH, HEIGHT = 1400, 420
FRAMES, DURATION = 96, 60
SCAN_FRAMES, SCAN_BAND = 64, 7
PORTRAIT_FONT, PORTRAIT_LINE = 7, 7
PORTRAIT_RIGHT = 40
RAMP = " .:-=+*#%@"
PORTRAIT = Path(__file__).resolve().parents[1] / "assets" / "portrait-ascii.txt"
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


def load_portrait() -> list[str]:
    lines = [line.rstrip("\n") for line in PORTRAIT.read_text().splitlines()]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    width = max(len(line) for line in lines)
    return [line.ljust(width) for line in lines]


def invert(lines: list[str]) -> list[str]:
    # The art is drawn for dark ink on light paper: swap the ramp for light ink.
    ink = RAMP[1:]
    table = str.maketrans(ink, ink[::-1])
    return [line.translate(table) for line in lines]


def scramble(line: str, rng: random.Random) -> str:
    return "".join(c if c == " " else rng.choice(RAMP[1:]) for c in line)


def mix(a: tuple[int, ...], b: tuple[int, ...], amount: float) -> tuple[int, ...]:
    return tuple(round(x + (y - x) * amount) for x, y in zip(a, b))


def tone(bg: tuple[int, ...], fg: tuple[int, ...], char: str) -> tuple[int, ...]:
    return mix(bg, fg, 0.22 + 0.78 * RAMP.index(char) / (len(RAMP) - 1))


def draw_portrait(draw: ImageDraw.ImageDraw, lines: list[str], xy: tuple[int, int],
                  font: ImageFont.FreeTypeFont, bg: tuple[int, ...],
                  fg: tuple[int, ...]) -> None:
    # One pass per ramp level keeps columns aligned while each glyph gets its own tone.
    for char in RAMP[1:]:
        for row, line in enumerate(lines):
            if char in line:
                layer = "".join(c if c == char else " " for c in line)
                draw.text((xy[0], xy[1] + row * PORTRAIT_LINE), layer, font=font,
                          fill=tone(bg, fg, char))


def render(output: Path, font_path: str | None) -> None:
    output.mkdir(parents=True, exist_ok=True)
    font = load_font(PORTRAIT_FONT, font_path)
    title = load_font(25, font_path)
    small = load_font(15, font_path)
    label = load_font(14, font_path)
    portrait = load_portrait()
    span = round(font.getlength(portrait[0]))
    left = WIDTH - PORTRAIT_RIGHT - span
    top = HEIGHT - 2 - len(portrait) * PORTRAIT_LINE

    for theme, bg, fg, lines in [
        ("dark", (13, 17, 23), (211, 224, 238), invert(portrait)),
        ("light", (246, 248, 250), (48, 64, 83), portrait),
    ]:
        rng = random.Random(11)
        palette = Image.new("P", (1, 1))
        colors = [v for i in range(256) for v in mix(bg, fg, i / 255)]
        palette.putpalette(colors)
        base = Image.new("RGB", (WIDTH, HEIGHT), bg)
        draw = ImageDraw.Draw(base)
        draw.rounded_rectangle((0, 0, WIDTH - 1, HEIGHT - 1), radius=16,
                               outline=mix(bg, fg, 0.2), width=2)
        draw.text((52, 31), "thiagoyb11@github:~$ whoami", font=small,
                  fill=mix(bg, fg, 0.65))
        draw.line((52, 72, left - 40, 72), fill=mix(bg, fg, 0.13))
        for row, text in enumerate(LETTERING):
            draw.text((52, 102 + row * 24), text, font=title, fill=mix(bg, fg, 0.96))
        draw.text((54, 297), "Y O R I S  B E R T S C H I", font=label,
                  fill=mix(bg, fg, 0.7))
        draw.text((54, 343), "Information Systems Engineering", font=small,
                  fill=mix(bg, fg, 0.72))
        draw.text((54, 369), "UTN Santa Fe / Argentina", font=label,
                  fill=mix(bg, fg, 0.51))
        draw_portrait(draw, lines, (left, top), font, bg, fg)
        frames = []
        for step in range(FRAMES):
            # The band enters above the art and leaves below it, so frame 0 is clean.
            front = step * (len(lines) + SCAN_BAND) / SCAN_FRAMES - 1
            frame = base.copy()
            ink = ImageDraw.Draw(frame)
            for row, line in enumerate(lines):
                if step < SCAN_FRAMES and 0 <= front - row < SCAN_BAND:
                    y = top + row * PORTRAIT_LINE
                    ink.rectangle((left, y, left + span, y + PORTRAIT_LINE - 1), fill=bg)
                    ink.text((left, y), scramble(line, rng), font=font, fill=fg)
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
