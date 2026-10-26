import os
import subprocess
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from NASS.nas_config import NasConfig


@contextmanager
def connect_to_nas() -> Iterator[Path]:
    """Connect to the configured NAS and yield its mapped drive path."""
    nas_config = NasConfig.load()
    nas_user = os.environ.get("NAS_USER")
    nas_pass = os.environ.get("NAS_PASS")

    if not nas_user or not nas_pass:
        raise RuntimeError("Define las variables de entorno NAS_USER y NAS_PASS.")

    subprocess.run(
        ["net", "use", nas_config.unidad_temp, "/delete", "/yes"],
        capture_output=True,
        text=True,
    )

    recurso_nas = f"\\\\{nas_config.nas_ip}\\{nas_config.nas_share}"
    resultado = subprocess.run(
        [
            "net",
            "use",
            nas_config.unidad_temp,
            recurso_nas,
            nas_pass,
            f"/user:{nas_user}",
        ],
        capture_output=True,
        text=True,
    )

    if resultado.returncode != 0:
        detalle = "\n".join(
            parte.strip() for parte in (resultado.stdout, resultado.stderr) if parte.strip()
        )
        raise RuntimeError(f"Error al conectar la unidad de red:\n{detalle}")

    try:
        yield Path(nas_config.unidad_temp + "\\")
    finally:
        resultado = subprocess.run(
            ["net", "use", nas_config.unidad_temp, "/delete", "/yes"],
            capture_output=True,
            text=True,
        )
        if resultado.returncode != 0:
            detalle = "\n".join(
                parte.strip()
                for parte in (resultado.stdout, resultado.stderr)
                if parte.strip()
            )
            raise RuntimeError(f"Error al desconectar la unidad de red:\n{detalle}")
