"""Check every theme's text colors against WCAG 2.1 AA (4.5:1).
Run with:  python3 -m unittest discover tests"""
import os
import re
import unittest

CSS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "css", "style.css")

# (foreground, background) pairs that appear together on the page.
PAIRS = [
    ("text", "bg"), ("text", "surface"), ("text", "stripe"), ("text", "hover"),
    ("muted", "bg"), ("muted", "surface"), ("muted", "stripe"), ("muted", "hover"),
    ("header-text", "header-bg"), ("link", "bg"), ("link", "surface"),
    ("mark-text", "mark-bg"), ("accent-text", "accent"),
]


def themes():
    with open(CSS, encoding="utf-8") as f:
        css = f.read()
    block = css.split("/* THEMES-START */")[1].split("/* THEMES-END */")[0]
    out = {}
    for name, body in re.findall(r'\[data-theme="([^"]+)"\]\s*\{(.*?)\}', block, re.S):
        out[name] = dict(re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{6})\s*;", body))
    return out


def luminance(hex_color):
    def channel(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def ratio(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


class ContrastTests(unittest.TestCase):
    def test_four_themes(self):
        self.assertEqual(sorted(themes()), ["deep-space", "enchanted-forest", "library-classic", "retro-pulp"])

    def test_aa_contrast(self):
        failures = []
        for name, colors in themes().items():
            for fg, bg in PAIRS:
                if fg not in colors or bg not in colors:
                    failures.append(f"{name}: missing --{fg} or --{bg}")
                    continue
                r = ratio(colors[fg], colors[bg])
                if r < 4.5:
                    failures.append(f"{name}: --{fg} on --{bg} is {r:.2f}:1 (needs 4.5)")
        self.assertEqual(failures, [], "\n" + "\n".join(failures))


if __name__ == "__main__":
    unittest.main()
