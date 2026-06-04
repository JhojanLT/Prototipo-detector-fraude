"""
Módulo 0 — Validación de nivel académico
Verifica si el título presentado corresponde a un pregrado universitario,
requisito mínimo para admisión a posgrado en Colombia (Ley 30 de 1992,
Decreto 1330 de 2019).

Niveles en Colombia:
  - Técnico profesional (2 años) → NO cumple
  - Tecnología (3 años)          → NO cumple
  - Pregrado universitario (4-5 años) → SÍ cumple
  - Especialización / Maestría / Doctorado → SÍ cumple (ya tiene pregrado)
"""

import json
import re
from anthropic import Anthropic

client = Anthropic()
MODEL = "claude-sonnet-4-20250514"

# Palabras clave que indican nivel universitario (SÍ cumple)
KEYWORDS_PREGRADO = [
    "ingeniero", "ingeniera",
    "abogado", "abogada",
    "médico", "médica", "medico", "medica",
    "enfermero", "enfermera",
    "psicólogo", "psicóloga", "psicologo", "psicologa",
    "administrador", "administradora",
    "contador", "contadora",
    "economista",
    "arquitecto", "arquitecta",
    "licenciado", "licenciada",
    "químico", "química", "quimico", "quimica",
    "biólogo", "bióloga", "biologo", "biologa",
    "fisioterapeuta",
    "odontólogo", "odontóloga", "odontologo", "odontologa",
    "nutricionista",
    "bacteriólogo", "bacterióloga",
    "trabajador social", "trabajadora social",
    "comunicador", "comunicadora",
    "diseñador", "diseñadora",
    "filósofo", "filósofa",
    "historiador", "historiadora",
    "geólogo", "geóloga",
    "título universitario",
    "titulo universitario",
    "pregrado",
    "especialista",
    "magíster", "magister",
    "doctor", "doctora",
]

# Palabras clave que indican nivel NO universitario (NO cumple)
KEYWORDS_NO_PREGRADO = [
    "tecnólogo", "tecnóloga", "tecnologo", "tecnologa",
    "tecnología en", "tecnologia en",
    "título de tecnólogo", "titulo de tecnologo",
    "técnico profesional", "tecnico profesional",
    "técnico en", "tecnico en",
    "título técnico", "titulo tecnico",
    "técnico laboral", "tecnico laboral",
]


def _check_keywords(text: str) -> str | None:
    """
    Primera verificación rápida por palabras clave antes de llamar a la IA.
    Devuelve 'cumple', 'no_cumple' o None si no hay certeza.
    """
    text_lower = text.lower()

    # Primero verificar si hay señales claras de NO cumplimiento
    for kw in KEYWORDS_NO_PREGRADO:
        if kw in text_lower:
            return "no_cumple"

    # Luego verificar señales de cumplimiento
    for kw in KEYWORDS_PREGRADO:
        if kw in text_lower:
            return "cumple"

    return None  # No hay certeza, necesita análisis con IA


def validate_academic_level(ocr_text: str) -> dict:
    """
    Módulo 0 — Validación de nivel académico.
    Analiza el texto del OCR para determinar si el título es de pregrado
    universitario o superior, requisito mínimo para posgrado en Colombia.

    Devuelve un dict con:
    - cumple_requisito: bool
    - nivel_detectado: str
    - titulo_detectado: str
    - programa_detectado: str
    - razon: str
    - confianza: str (alta|media|baja)
    """
    # Intento rápido por palabras clave primero (sin gastar tokens de API)
    resultado_rapido = _check_keywords(ocr_text)

    if resultado_rapido == "no_cumple":
        # Detectado por keyword — confirmamos con IA para más detalle
        pass  # igual llamamos a la IA para obtener el nivel específico
    elif resultado_rapido == "cumple" and len(ocr_text.strip()) < 20:
        # Texto muy corto y parece pregrado — respuesta rápida
        return {
            "cumple_requisito": True,
            "nivel_detectado": "pregrado universitario",
            "titulo_detectado": "no identificado (texto insuficiente)",
            "programa_detectado": "no identificado (texto insuficiente)",
            "razon": "El texto extraído sugiere un título universitario pero es insuficiente para análisis completo.",
            "confianza": "baja",
        }

    # Análisis con IA para mayor precisión
    prompt = f"""Eres un experto en el sistema de educación superior colombiano. Tu tarea es determinar si el título académico descrito en el siguiente texto cumple el requisito mínimo de admisión a un programa de posgrado (especialización, maestría o doctorado) en Colombia.

SISTEMA DE NIVELES EN COLOMBIA (Ley 30 de 1992, Decreto 1330 de 2019):
- Técnico profesional (2 años): NO cumple requisito de posgrado
- Tecnólogo / Tecnología (3 años): NO cumple requisito de posgrado universitario
- Pregrado universitario / Profesional (4-5 años): SÍ cumple
- Especialización, Maestría, Doctorado: SÍ cumple (ya tienen pregrado)

TEXTO EXTRAÍDO DEL TÍTULO POR OCR (puede estar fragmentado o incompleto):
---
{ocr_text}
---

IMPORTANTE sobre el texto:
- El OCR puede haber leído mal algunas palabras por fuentes decorativas del diploma
- Si el texto es muy fragmentado, infiere el nivel con base en las palabras reconocibles
- Si no hay suficiente información para determinar el nivel, indica confianza baja

Analiza el texto e identifica:
1. El título o grado otorgado (ej: "Ingeniero de Sistemas", "Tecnólogo en Informática")
2. El programa académico
3. Si ese título cumple el requisito de pregrado universitario para acceder a posgrado en Colombia

Responde ÚNICAMENTE en formato JSON válido:
{{
  "cumple_requisito": true|false,
  "nivel_detectado": "técnico profesional|tecnólogo|pregrado universitario|especialización|maestría|doctorado|no identificado",
  "titulo_detectado": "título exacto como aparece en el documento o 'no identificado'",
  "programa_detectado": "nombre del programa o 'no identificado'",
  "razon": "explicación clara de por qué cumple o no cumple el requisito, en 1-2 oraciones",
  "confianza": "alta|media|baja"
}}

Si el texto es demasiado fragmentado para determinar el nivel con certeza, indica cumple_requisito como true con confianza baja (ante la duda, no bloquear — el funcionario humano debe decidir)."""

    message = client.messages.create(
        model=MODEL,
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}],
    )

    result = _parse_json(message.content[0].text)

    # Doble verificación: si la IA dice que cumple pero hay keyword de no cumplimiento
    if result.get("cumple_requisito") and resultado_rapido == "no_cumple":
        result["cumple_requisito"] = False
        result["confianza"] = "media"
        result["razon"] = (
            "Se detectaron términos asociados a nivel tecnológico o técnico. "
            + result.get("razon", "")
        )

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
            return json.loads(text[start : end + 1])
        # Fallback seguro: ante error, no bloquear
        return {
            "cumple_requisito": True,
            "nivel_detectado": "no identificado",
            "titulo_detectado": "no identificado",
            "programa_detectado": "no identificado",
            "razon": "No fue posible analizar el nivel académico por limitaciones del texto extraído. El funcionario debe verificar manualmente.",
            "confianza": "baja",
        }
