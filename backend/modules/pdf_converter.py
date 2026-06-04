"""
Utilidad de conversión PDF → imagen
Usa pdf2image (wrapper de poppler) para convertir la primera página
de un PDF a imagen PNG procesable por el sistema.

Instalación de poppler en Windows:
1. Descargar desde: https://github.com/oschwartz10612/poppler-windows/releases
2. Extraer y agregar la carpeta bin/ al PATH (igual que Tesseract)
"""

import io
from PIL import Image


def pdf_to_image_bytes(pdf_bytes: bytes, dpi: int = 200) -> bytes:
    """
    Convierte la primera página de un PDF a bytes de imagen PNG.
    dpi=200 es suficiente para OCR y análisis visual sin ser demasiado pesado.
    """
    try:
        from pdf2image import convert_from_bytes
    except ImportError:
        raise RuntimeError(
            "pdf2image no está instalado. Ejecuta: pip install pdf2image"
        )

    try:
        pages = convert_from_bytes(pdf_bytes, dpi=dpi, first_page=1, last_page=1)
    except Exception as e:
        raise RuntimeError(
            f"No se pudo convertir el PDF. Verifica que poppler esté instalado y en el PATH. Error: {e}"
        )

    if not pages:
        raise ValueError("El PDF no contiene páginas o está vacío.")

    # Tomar solo la primera página
    page = pages[0]

    # Convertir PIL Image a bytes PNG
    buffer = io.BytesIO()
    page.save(buffer, format="PNG")
    return buffer.getvalue()


def is_pdf(content_type: str, filename: str) -> bool:
    """Determina si el archivo subido es un PDF."""
    return (
        content_type == "application/pdf"
        or filename.lower().endswith(".pdf")
    )
