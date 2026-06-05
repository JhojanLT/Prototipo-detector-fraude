"""
Módulo 0 — Validación de documento y nivel académico
Primero verifica VISUALMENTE si el documento es un diploma/título académico,
usando la imagen directamente (no depende del OCR).
Si es diploma, verifica que corresponda a un pregrado universitario,
requisito mínimo para admisión a posgrado en Colombia (Ley 30 de 1992,
Decreto 1330 de 2019).
"""

import base64
import json
from anthropic import Anthropic

client = Anthropic()
MODEL = "claude-sonnet-4-6"

# Palabras que indican claramente que NO es un diploma (señales fuertes en el OCR)
KEYWORDS_NO_DIPLOMA = [
    "cédula de ciudadanía", "cedula de ciudadania",
    "tarjeta de identidad",
    "número de identificación", "numero de identificacion",
    "registro civil",
    "fecha de nacimiento",
    "lugar de nacimiento",
    "registraduría", "registraduria",
    "tabla de contenido",
    "isbn",
    "derechos reservados", "todos los derechos",
    "impreso en",
]

# Palabras que indican nivel NO universitario
KEYWORDS_NO_PREGRADO = [
    "tecnólogo", "tecnóloga", "tecnologo", "tecnologa",
    "tecnología en", "tecnologia en",
    "título de tecnólogo", "titulo de tecnologo",
    "técnico profesional", "tecnico profesional",
    "técnico en", "tecnico en",
    "título técnico", "titulo tecnico",
    "técnico laboral", "tecnico laboral",
]


def _keywords_no_diploma(text: str) -> bool:
    """Retorna True si el texto contiene señales inequívocas de no ser un diploma."""
    text_lower = text.lower()
    return any(kw in text_lower for kw in KEYWORDS_NO_DIPLOMA)


def _keywords_no_pregrado(text: str) -> bool:
    """Retorna True si el texto contiene señales de nivel técnico/tecnólogo."""
    text_lower = text.lower()
    return any(kw in text_lower for kw in KEYWORDS_NO_PREGRADO)


def validate_academic_level(ocr_text: str, image_bytes: bytes) -> dict:
    """
    Módulo 0 — Validación de documento y nivel académico.
    Usa la imagen directamente para determinar si es un diploma, sin depender
    únicamente del OCR (que falla con fuentes decorativas de diplomas colombianos).

    Args:
        ocr_text: Texto extraído por Tesseract (puede estar fragmentado)
        image_bytes: Bytes de la imagen procesada (JPEG) para análisis visual

    Retorna dict con:
        es_diploma, cumple_requisito, nivel_detectado, titulo_detectado,
        programa_detectado, razon, confianza
    """
    # Señal fuerte por keywords: si el texto dice explícitamente que es otro documento
    if _keywords_no_diploma(ocr_text):
        return {
            "es_diploma": False,
            "cumple_requisito": False,
            "nivel_detectado": "no aplica",
            "titulo_detectado": "no aplica",
            "programa_detectado": "no aplica",
            "razon": "El texto extraído contiene indicadores claros de que no es un diploma (cédula, libro u otro documento).",
            "confianza": "alta",
        }

    # Análisis visual con la imagen — más confiable que solo el OCR
    img_b64 = base64.standard_b64encode(image_bytes).decode("utf-8")

    prompt = f"""Eres un experto en documentos académicos colombianos. Analiza esta imagen y el texto OCR adjunto para determinar:

1. ¿ES este documento un diploma o título académico universitario?
2. Si es diploma, ¿qué nivel académico otorga y cumple el requisito mínimo de pregrado para posgrado en Colombia?

SISTEMA DE NIVELES EN COLOMBIA (Ley 30 de 1992):
- Técnico profesional: NO cumple
- Tecnólogo / Tecnología: NO cumple
- Pregrado universitario / Profesional: SÍ cumple
- Especialización, Maestría, Doctorado: SÍ cumple

TEXTO OCR EXTRAÍDO (puede estar fragmentado por fuentes decorativas — es normal en diplomas colombianos):
---
{ocr_text if ocr_text.strip() else "(sin texto legible por OCR)"}
---

INSTRUCCIONES:
- Analiza PRINCIPALMENTE la imagen. Los diplomas colombianos tienen: membrete institucional, sello, firmas de rector/decano, nombre del graduado, título otorgado, fecha.
- El OCR fragmentado NO es razón para decir que no es diploma. Los diplomas usan fuentes caligráficas que el OCR lee mal.
- Marca es_diploma=false SOLO si la imagen claramente NO es un diploma (cédula, pasaporte, libro, contrato, etc.).
- Si hay duda razonable de que podría ser un diploma (imagen borrosa, recortada, etc.), marca es_diploma=true con confianza baja.
- Para el nivel: si no puedes determinarlo con certeza, pon cumple_requisito=true con confianza baja.

Responde ÚNICAMENTE en formato JSON:
{{
  "es_diploma": true|false,
  "cumple_requisito": true|false,
  "nivel_detectado": "técnico profesional|tecnólogo|pregrado universitario|especialización|maestría|doctorado|no aplica|no identificado",
  "titulo_detectado": "título otorgado o 'no identificado'",
  "programa_detectado": "nombre del programa o 'no identificado'",
  "razon": "explicación breve de la decisión en 1-2 oraciones",
  "confianza": "alta|media|baja"
}}"""

    message = client.messages.create(
        model=MODEL,
        max_tokens=800,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": img_b64,
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    )

    result = _parse_json(message.content[0].text)

    # Doble verificación: si la IA dice que cumple nivel pero hay keyword de técnico/tecnólogo
    if result.get("cumple_requisito") and _keywords_no_pregrado(ocr_text):
        result["cumple_requisito"] = False
        result["confianza"] = "media"
        result["razon"] = (
            "Se detectaron términos de nivel tecnológico o técnico en el texto. "
            + result.get("razon", "")
        )

    # Coherencia: si no es diploma, no puede cumplir requisito
    if not result.get("es_diploma", True):
        result["cumple_requisito"] = False

    return result


def _parse_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(text[start: end + 1])
            except json.JSONDecodeError:
                pass
        # Fallback: ante error de parseo, no bloquear
        return {
            "es_diploma": True,
            "cumple_requisito": True,
            "nivel_detectado": "no identificado",
            "titulo_detectado": "no identificado",
            "programa_detectado": "no identificado",
            "razon": "No fue posible analizar el documento. El funcionario debe verificar manualmente.",
            "confianza": "baja",
        }
