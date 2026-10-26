import shutil
from pathlib import Path
from typing import Iterable

from NASS.nas_connection import connect_to_nas


DEFAULT_NAS_DESTINATION = Path(".")


def list_nas_directories(relative_folder: Path = Path(".")) -> list[str]:
    """Return the names of immediate subdirectories in a NAS folder."""
    relative_folder = Path(relative_folder)
    if relative_folder.is_absolute() or ".." in relative_folder.parts:
        raise ValueError("La carpeta debe estar dentro del recurso compartido.")

    with connect_to_nas() as nas_path:
        folder_path = nas_path / relative_folder
        if not folder_path.is_dir():
            raise FileNotFoundError(f"No existe la carpeta del NAS: {relative_folder}")
        return sorted(child.name for child in folder_path.iterdir() if child.is_dir())


def copy_files_to_nas(
    files: Iterable[Path],
    destination_folder: Path = DEFAULT_NAS_DESTINATION,
) -> list[Path]:
    """Copy local files into a folder relative to the configured NAS share."""
    source_files = [Path(file_path) for file_path in files]
    if not source_files:
        raise ValueError("Selecciona al menos un archivo para copiar.")

    relative_destination = Path(destination_folder)
    if relative_destination.is_absolute() or ".." in relative_destination.parts:
        raise ValueError("La carpeta de destino debe estar dentro del recurso compartido.")

    for source_file in source_files:
        if not source_file.is_file():
            raise FileNotFoundError(f"No se encontró el archivo: {source_file}")

    with connect_to_nas() as nas_path:
        destination_path = nas_path / relative_destination
        destination_path.mkdir(parents=True, exist_ok=True)
        copied_files = []
        for source_file in source_files:
            copied_file = destination_path / source_file.name
            shutil.copy2(source_file, copied_file)
            copied_files.append(copied_file)

    return copied_files
