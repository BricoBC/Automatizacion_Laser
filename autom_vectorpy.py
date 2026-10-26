from pathlib import Path

import vtracer


def convert_png_to_svg(png_path: Path, svg_path: Path) -> Path:
    """Convert a PNG image to SVG using the project's binary tracing settings."""
    png_path = Path(png_path)
    svg_path = Path(svg_path)

    if png_path.suffix.lower() != ".png":
        raise ValueError("El archivo de entrada debe ser una imagen PNG.")
    if not png_path.is_file():
        raise FileNotFoundError(f"No se encontró la imagen: {png_path}")
    if svg_path.suffix.lower() != ".svg":
        raise ValueError("El archivo de salida debe tener extensión .svg.")

    svg_path.parent.mkdir(parents=True, exist_ok=True)
    vtracer.convert_image_to_svg_py(
        str(png_path),
        str(svg_path),
        colormode="binary",
        hierarchical="stacked",
    )
    return svg_path
