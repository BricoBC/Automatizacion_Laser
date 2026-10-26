from pathlib import Path
from tempfile import TemporaryDirectory

import streamlit as st

from autom_vectorpy import convert_png_to_svg
from nas_file_operations import DEFAULT_NAS_DESTINATION, copy_files_to_nas


st.set_page_config(page_title="Operaciones de imágenes", page_icon="🖼️")
st.title("Operaciones de imágenes")
st.write("Selecciona un PNG para copiarlo al NAS, vectorizarlo o hacer ambas cosas.")

uploaded_file = st.file_uploader(
    "Selecciona una imagen PNG",
    type=["png"],
)

if uploaded_file is not None:
    st.image(uploaded_file.getvalue(), caption=uploaded_file.name)

operation = st.radio(
    "¿Qué quieres hacer?",
    (
        "Convertir a SVG y copiar",
        "Copiar el PNG original",
        "Copiar el PNG y el SVG",
    ),
)
destination = st.text_input(
    "Carpeta destino dentro del NAS",
    value=str(DEFAULT_NAS_DESTINATION),
    help="La ruta debe ser relativa al recurso compartido del NAS.",
)

if st.button("Procesar imagen", type="primary"):
    if uploaded_file is None:
        st.error("Selecciona una imagen PNG antes de continuar.")
    elif not uploaded_file.name.lower().endswith(".png"):
        st.error("El archivo seleccionado debe tener extensión PNG.")
    else:
        try:
            with TemporaryDirectory(prefix="automatizacion_laser_") as temp_dir:
                temp_path = Path(temp_dir)
                png_path = temp_path / Path(uploaded_file.name).name
                png_path.write_bytes(uploaded_file.getvalue())

                files_to_copy = []
                svg_content = None
                if operation in ("Copiar el PNG original", "Copiar el PNG y el SVG"):
                    files_to_copy.append(png_path)

                if operation in ("Convertir a SVG y copiar", "Copiar el PNG y el SVG"):
                    svg_path = temp_path / f"{png_path.stem}.svg"
                    convert_png_to_svg(png_path, svg_path)
                    files_to_copy.append(svg_path)
                    svg_content = svg_path.read_bytes()

                copied_files = copy_files_to_nas(files_to_copy, Path(destination))

            st.success("Operación completada. Archivos copiados al NAS:")
            for copied_file in copied_files:
                st.write(str(copied_file))

            if svg_content is not None:
                st.download_button(
                    "Descargar el SVG generado",
                    data=svg_content,
                    file_name=f"{Path(uploaded_file.name).stem}.svg",
                    mime="image/svg+xml",
                )
        except (OSError, RuntimeError, ValueError) as error:
            st.error(f"No se pudo completar la operación: {error}")
