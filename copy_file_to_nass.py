import os
from pathlib import Path

from nas_file_operations import copy_files_to_nas


def main(nombre_archivo: str):
    user_profile = Path(os.path.expanduser("~"))
    downloads_folder = user_profile / "Downloads"
    if not downloads_folder.exists():
        downloads_folder = user_profile / "Descargas"

    source_file = downloads_folder / nombre_archivo
    print(f"Buscando archivo en: {source_file}")
    copied_files = copy_files_to_nas([source_file])
    print(f"🎉 ¡Archivo copiado exitosamente al NAS: {copied_files[0]}!")

if __name__ == "__main__":
    main("tu_imagen.jpg")