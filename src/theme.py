THEMES = {
    "dark": {
        "bg": "#0a0e14",
        "panel": "#10151d",
        "border": "#232a36",
        "text": "#dfe3ea",
        "muted": "#6b7280",
        "green": "#2ecc71",
        "amber": "#f0a500",
        "red": "#e74c3c",
        "blue": "#4fc3f7",
        "cyan": "#00d4d4",
    },
    "light": {
        "bg": "#f4f5f7",
        "panel": "#ffffff",
        "border": "#d7dbe2",
        "text": "#1a1d23",
        "muted": "#6b7280",
        "green": "#1a9850",
        "amber": "#b8720a",
        "red": "#c0392b",
        "blue": "#1565c0",
        "cyan": "#007a7a",
    },
}


def get_theme(name):
    return THEMES.get(name, THEMES["dark"])
