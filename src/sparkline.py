def sparkline_svg(values, color, width=90, height=28, stroke_width=1.5):
    """Inline SVG sparkline for a numeric sequence. No JS/Plotly dependency
    so KPI cards stay cheap to render (4 extra Plotly charts would not)."""
    clean = [v for v in values if v == v]  # drop NaN
    if len(clean) < 2:
        return ""

    vmin, vmax = min(clean), max(clean)
    span = (vmax - vmin) or 1
    n = len(clean)
    points = [
        f"{(i / (n - 1)) * width:.1f},{height - ((v - vmin) / span) * height:.1f}"
        for i, v in enumerate(clean)
    ]
    polyline = " ".join(points)

    return (
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        f'preserveAspectRatio="none" style="display:block;">'
        f'<polyline points="{polyline}" fill="none" stroke="{color}" '
        f'stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"/>'
        f"</svg>"
    )
