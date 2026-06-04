"""
Módulo 1 — Preprocesamiento documental
Recibe la imagen escaneada del título y la prepara para el análisis.
Aplica técnicas de mejora de imagen inspiradas en LTHE (Bae et al., 2025b):
eliminación de ruido, mejora de contraste, binarización y enderezado.
"""

import cv2
import numpy as np
from typing import Tuple


def deskew(image: np.ndarray) -> np.ndarray:
    """Endereza la imagen si está rotada, usando el ángulo del texto detectado."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    # Invertir para que el texto sea blanco sobre negro
    gray = cv2.bitwise_not(gray)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    coords = np.column_stack(np.where(thresh > 0))
    if len(coords) < 10:
        return image
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    # Solo corregir si el ángulo es significativo
    if abs(angle) < 0.5:
        return image
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(
        image, M, (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE,
    )


def enhance_contrast_lthe(gray: np.ndarray) -> np.ndarray:
    """
    Aproximación a LTHE (Local Texture and Histogram Equalization).
    Combina CLAHE (ecualización adaptativa local) con realce de textura
    para amplificar cambios sutiles de píxel en regiones potencialmente alteradas.
    """
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    equalized = clahe.apply(gray)
    # Realce de textura mediante filtro de nitidez
    kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    sharpened = cv2.filter2D(equalized, -1, kernel)
    return sharpened


def denoise(gray: np.ndarray) -> np.ndarray:
    """Elimina ruido preservando bordes (importante para análisis tipográfico)."""
    return cv2.fastNlMeansDenoising(gray, None, h=10, templateWindowSize=7, searchWindowSize=21)


def preprocess_document(image_bytes: bytes) -> Tuple[np.ndarray, dict]:
    """
    Pipeline completo del Módulo 1.
    Devuelve la imagen procesada y un diccionario con metadatos del procesamiento.
    """
    # Decodificar imagen desde bytes
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("No se pudo decodificar la imagen. Verifique el formato.")

    original_shape = image.shape
    steps = []

    # 1. Enderezado
    image = deskew(image)
    steps.append("Enderezado (deskew)")

    # 2. Conversión a escala de grises
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    steps.append("Conversión a escala de grises")

    # 3. Eliminación de ruido
    gray = denoise(gray)
    steps.append("Eliminación de ruido (Non-local Means)")

    # 4. Mejora de contraste tipo LTHE
    enhanced = enhance_contrast_lthe(gray)
    steps.append("Mejora de contraste (CLAHE + realce de textura)")

    # 5. Normalización
    normalized = cv2.normalize(enhanced, None, 0, 255, cv2.NORM_MINMAX)
    steps.append("Normalización de intensidad")

    metadata = {
        "dimensiones_originales": f"{original_shape[1]}x{original_shape[0]} px",
        "pasos_aplicados": steps,
        "modulo": "Módulo 1 — Preprocesamiento documental",
    }

    return normalized, metadata


def to_png_bytes(image: np.ndarray) -> bytes:
    """Convierte una imagen procesada a bytes PNG para envío o visualización."""
    success, buffer = cv2.imencode(".png", image)
    if not success:
        raise ValueError("Error al codificar la imagen procesada.")
    return buffer.tobytes()
