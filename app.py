from pathlib import Path
from tempfile import TemporaryDirectory

import streamlit as st

from autom_vectorpy import convert_png_to_svg
from nas_file_operations import (
    DEFAULT_NAS_DESTINATION,
    copy_files_to_nas,
    list_nas_directories,
)


st.set_page_config(page_title="Operaciones de imágenes", page_icon="🖼️")
st.title("Operaciones de imágenes")
st.write("Selecciona un PNG para copiarlo al NAS, vectorizarlo o hacer ambas cosas.")

uploaded_file = st.file_uploader(
    "Selecciona una imagen PNG",
    type=["png"],
)

if uploaded_file is not None:
    st.image(uploaded_file.getvalue(), caption=uploaded_file.name, width=300)

operation = st.radio(
    "¿Qué quieres hacer?",
    (
        "Convertir a SVG y copiar",
        "Copiar el PNG original",
        "Copiar el PNG y el SVG",
    ),
)
st.subheader("Carpeta destino en el NAS")
st.session_state.setdefault("nas_current_folder", DEFAULT_NAS_DESTINATION)
st.session_state.setdefault("nas_selected_folder", DEFAULT_NAS_DESTINATION)
if st.session_state["nas_selected_folder"] is None:
    st.session_state["nas_selected_folder"] = DEFAULT_NAS_DESTINATION

current_folder = Path(st.session_state["nas_current_folder"])
st.caption(f"Carpeta actual dentro del recurso compartido: {current_folder}")
try:
    directories = list_nas_directories(current_folder)
except (OSError, RuntimeError, ValueError) as error:
    st.error(f"No se pudieron consultar las carpetas del NAS: {error}")
    directories = []

col_navigate, col_choose = st.columns(2)
with col_navigate:
    if current_folder != Path(".") and st.button("⬆️ Subir un nivel"):
        st.session_state["nas_current_folder"] = current_folder.parent
        st.rerun()

    selected_directory = st.selectbox(
        "Carpetas disponibles",
        options=[""] + directories,
        format_func=lambda folder: folder or "Selecciona una carpeta para abrir",
        key=f"nas_directory_{current_folder}",
    )
    if st.button("Abrir carpeta", disabled=not selected_directory):
        st.session_state["nas_current_folder"] = current_folder / selected_directory
        st.rerun()

with col_choose:
    if st.button("Usar esta carpeta como destino"):
        st.session_state["nas_selected_folder"] = current_folder

destination = st.session_state["nas_selected_folder"]
if destination is None:
    st.info("Navega hasta la carpeta deseada y selecciónala como destino.")
else:
    st.success(f"Destino seleccionado: {destination}")

if st.button("Procesar imagen", type="primary"):
    if uploaded_file is None:
        st.error("Selecciona una imagen PNG antes de continuar.")
    elif not uploaded_file.name.lower().endswith(".png"):
        st.error("El archivo seleccionado debe tener extensión PNG.")
    elif destination is None:
        st.error("Selecciona una carpeta destino en el NAS antes de continuar.")
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

                copied_files = copy_files_to_nas(files_to_copy, destination)

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
