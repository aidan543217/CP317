# accessibility.py
import json
from pathlib import Path

SETTINGS_PATH = Path(__file__).parent / "user_settings.json"

DEFAULT_SETTINGS = {
    "font_scale": 1.0,          # 0.8 to 1.6
    "theme": "light",           # "light" or "dark"
    "high_contrast": False,
    "base_font_family": "Arial",
}

def load_settings():
    if SETTINGS_PATH.exists():
        try:
            with open(SETTINGS_PATH) as f:
                saved = json.load(f)
            return {**DEFAULT_SETTINGS, **saved}
        except Exception:
            pass
    return dict(DEFAULT_SETTINGS)

def save_settings(settings):
    try:
        with open(SETTINGS_PATH, "w") as f:
            json.dump(settings, f, indent=2)
    except OSError as e:
        print(f"[!] Could not save settings: {e}")

def get_theme_colors(settings):
    """Return background/foreground/accent colors based on theme + contrast."""
    if settings["high_contrast"]:
        return {
            "bg": "#000000",
            "fg": "#FFFFFF",
            "button_bg": "#FFFF00",
            "button_fg": "#000000",
            "entry_bg": "#FFFFFF",
            "entry_fg": "#000000",
        }
    if settings["theme"] == "dark":
        return {
            "bg": "#2B2B2B",
            "fg": "#E8E8E8",
            "button_bg": "#4A4A4A",
            "button_fg": "#FFFFFF",
            "entry_bg": "#3C3C3C",
            "entry_fg": "#FFFFFF",
        }
    return {
        "bg": "#FFFFFF",
        "fg": "#000000",
        "button_bg": "#E0E0E0",
        "button_fg": "#000000",
        "entry_bg": "#FFFFFF",
        "entry_fg": "#000000",
    }

def get_font(settings, size=11, bold=False):
    family = settings["base_font_family"]
    scaled = max(8, int(size * settings["font_scale"]))
    return (family, scaled, "bold" if bold else "normal")