"""Descarga modelos ONNX oficiales de OpenCV Zoo para BioVerify-Zero v2.

Los modelos se descargan durante el build Docker para que la aplicación pueda
ejecutar YuNet + SFace sin depender de internet en tiempo de ejecución.
"""

from __future__ import annotations

import os
from pathlib import Path
from urllib.request import urlretrieve


MODELS = {
    "models/face_detection_yunet_2023mar.onnx": (
        "https://github.com/opencv/opencv_zoo/raw/main/models/"
        "face_detection_yunet/face_detection_yunet_2023mar.onnx"
    ),
    "models/face_recognition_sface_2021dec.onnx": (
        "https://github.com/opencv/opencv_zoo/raw/main/models/"
        "face_recognition_sface/face_recognition_sface_2021dec.onnx"
    ),
}


def download_file(target: Path, url: str) -> None:
    """Descarga un archivo si no existe o si está vacío."""
    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists() and target.stat().st_size > 0:
        print(f"Modelo ya existe: {target}")
        return

    print(f"Descargando {url} -> {target}")
    urlretrieve(url, target)

    if not target.exists() or target.stat().st_size == 0:
        raise RuntimeError(f"No se pudo descargar el modelo: {target}")


def main() -> None:
    """Descarga todos los modelos requeridos."""
    project_root = Path(os.getenv("BIOVERIFY_PROJECT_ROOT", ".")).resolve()

    for relative_path, url in MODELS.items():
        download_file(project_root / relative_path, url)

    print("Modelos descargados correctamente.")


if __name__ == "__main__":
    main()
