"""
Módulo 3 (parte OCR) — Extracción de texto
Usa Tesseract OCR con soporte en español para extraer el contenido textual
del título escaneado (Ortega Cuevas, 2024; García Rodríguez, 2024).
El texto extraído se analiza posteriormente con modelos de lenguaje.
"""

import pytesseract
import cv2
import numpy as np
from typing import Tuple


def extract_text(image: np.ndarray) -> Tuple[str, dict]:
    """
    Extrae texto de la imagen preprocesada usando Tesseract en español.
    Devuelve el texto y metadatos de confianza del OCR.
    """
    # Binarización Otsu para optimizar el OCR
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    # Configuración de Tesseract: español, modo de segmentación automática
    config = "--oem 3 --psm 3 -l spa"
    text = pytesseract.image_to_string(binary, config=config)

    # Obtener datos de confianza por palabra
    data = pytesseract.image_to_data(
        binary, config=config, output_type=pytesseract.Output.DICT
    )
    confidences = [int(c) for c in data["conf"] if int(c) > 0]
    avg_confidence = round(sum(confidences) / len(confidences), 2) if confidences else 0.0
    word_count = len([w for w in data["text"] if w.strip()])

    metadata = {
        "confianza_promedio_ocr": f"{avg_confidence}%",
        "palabras_detectadas": word_count,
        "motor": "Tesseract 5.x (idioma: español)",
        "modulo": "Módulo 3 — Extracción de texto (OCR)",
    }

    return text.strip(), metadata
