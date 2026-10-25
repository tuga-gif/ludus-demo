"""Turn a Ludus-style theme recipe into CSS custom properties.

Simplified example. A theme starts from three colours (background, text and
accent) and the rest is derived from them. The launcher also handles fonts,
corners, backgrounds and status colours.
"""


def hex_to_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def relative_luminance(rgb):
    def channel(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(a, b):
    """WCAG contrast ratio between two hex colours, from 1.0 to 21.0."""
    light, dark = sorted((relative_luminance(hex_to_rgb(a)),
                          relative_luminance(hex_to_rgb(b))), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def mix(a, b, amount):
    """Mix colour b into colour a. 0 keeps a, 1 gives b."""
    ra, rb = hex_to_rgb(a), hex_to_rgb(b)
    return "#" + "".join(f"{round(x + (y - x) * amount):02x}" for x, y in zip(ra, rb))


def theme_to_css(recipe):
    bg, text, accent = recipe["background"], recipe["text"], recipe["accent"]
    variables = {
        "--bg": bg,
        "--surface": mix(bg, text, 0.06),
        "--surface-hover": mix(bg, text, 0.10),
        "--border": mix(bg, text, 0.14),
        "--text": text,
        "--text-muted": mix(text, bg, 0.35),
        "--accent": accent,
        "--radius": f"{recipe.get('radius', 12)}px",
    }
    body = "\n".join(f"  {name}: {value};" for name, value in variables.items())
    return ":root {\n" + body + "\n}"


if __name__ == "__main__":
    midnight = {"background": "#0f1020", "text": "#e8e6ff", "accent": "#7c5cff", "radius": 14}
    print(theme_to_css(midnight))
    ratio = contrast_ratio(midnight["text"], midnight["background"])
    verdict = "easy to read" if ratio >= 7 else "readable" if ratio >= 4.5 else "too low"
    print(f"\nText contrast: {ratio:.1f}:1 ({verdict})")
