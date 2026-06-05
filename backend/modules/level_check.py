"""
Módulo 0 — Validación de documento y nivel académico
Primero verifica si el documento es un diploma/título académico.
Si lo es, verifica que corresponda a un pregrado universitario,
requisito mínimo para admisión a posgrado en Colombia (Ley 30 de 1992,
Decreto 1330 de 2019).

Niveles en Colombia:
  - Técnico profesional (2 años) → NO cumple
  - Tecnología (3 años)          → NO cumple
  - Pregrado universitario (4-5 años) → SÍ cumple
  - Especialización / Maestría / Doctorado → SÍ cumple (ya tiene pregrado)
"""

import json
from anthropic import Anthropic

client = Anthropic()
MODEL = "claude-sonnet-4-20250514"

# Palabras clave que confirman que es un diploma
KEYWORDS_DIPLOMA = [
    "título de", "titulo de",
    "grado de", "otorga el grado",
    "conferido el grado", "confiere el título",
    "ha culminado satisfactoriamente",
    "cumplido los requisitos",
    "acredita que",
    "universidad", "facultad", "escuela superior",
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
    "título universitario", "titulo universitario",
    "pregrado", "especialista", "magíster", "magister",
    "tecnólogo", "tecnóloga", "tecnologo", "tecnologa",
    "técnico profesional", "tecnico profesional",
    "técnico en", "tecnico en",
    "rector", "decano", "secretaria general",
    "acta de grado", "resolución de grado",
]

# Palabras que indican claramente que NO es un diploma
KEYWORDS_NO_DIPLOMA = [
    "cédula de ciudadanía", "cedula de ciudadania",
    "tarjeta de identidad",
    "pasaporte",
    "número de identificación", "numero de identificacion",
    "registro civil",
    "fecha de nacimiento",
    "lugar de nacimiento",
    "firma del titular",
    "registraduría", "registraduria",
    "república de colombia",  # aparece en cédulas, no en diplomas
    "tabla de contenido",
    "índice", "capítulo", "chapter",
    "isbn", "editorial",
    "prólogo", "introducción al libro",
    "derechos reservados", "todos los derechos",
    "impreso en",
]

# Palabras que indican nivel NO universitario (para la segunda verificación)
KEYWORDS_NO_PREGRADO = [
    "tecnólogo", "tecnóloga", "tecnologo", "tecnologa",
    "tecnología en", "tecnologia en",
    "título de tecnólogo", "titulo de tecnologo",
    "técnico profesional", "tecnico profesional",
    "técnico en", "tecnico en",
    "título técnico", "titulo tecnico",
    "técnico laboral", "tecnico laboral",
]


def _check_keywords(text: str) -> tuple[str | None, str | None]:
    """
    Verificación rápida por palabras clave.
    Devuelve (resultado_diploma, resultado_nivel):
      - resultado_diploma: 'es_diploma' | 'no_es_diploma' | None
      - resultado_nivel: 'cumple' | 'no_cumple' | None
    """
    text_lower = text.lower()

    # Detectar documentos claramente NO diploma
    for kw in KEYWORDS_NO_DIPLOMA:
        if kw in text_lower:
            return ("no_es_diploma", None)

    # Detectar si hay indicios de que es un diploma
    es_diploma = any(kw in text_lower for kw in KEYWORDS_DIPLOMA)
    resultado_diploma = "es_diploma" if es_diploma else None

    # Detectar nivel académico si hay indicios de diploma
    resultado_nivel = None
    if es_diploma:
        for kw in KEYWORDS_NO_PREGRADO:
            if kw in text_lower:
                resultado_nivel = "no_cumple"
                break
        else:
            resultado_nivel = "cumple"

    return (resultado_diploma, resultado_nivel)


def validate_academic_level(ocr_text: str) -> dict:
    """
    Módulo 0 — Validación de documento y nivel académico.
    Primero verifica si el documento es un diploma.
    Si lo es, verifica si cumple el requisito de nivel universitario.

    Devuelve un dict con:
    - es_diploma: bool
    - cumple_requisito: bool
    - nivel_detectado: str
    - titulo_detectado: str
    - programa_detectado: str
    - razon: str
    - confianza: str (alta|media|baja)
    """
    resultado_diploma_kw, resultado_nivel_kw = _check_keywords(ocr_text)

    # Si por keywords es claramente NO diploma, igual consultamos la IA para confirmación
    # pero ya tenemos una señal fuerte. Si el texto es muy corto, vamos directo a IA.

    prompt = f"""Eres un experto en documentos académicos colombianos. Debes analizar el siguiente texto extraído por OCR y determinar DOS cosas:

1. ¿ES este documento un diploma o título académico?
2. Si es diploma, ¿cumple el nivel mínimo para posgrado en Colombia?

TIPOS DE DOCUMENTOS QUE NO SON DIPLOMAS (ejemplos):
- Cédulas de ciudadanía o documentos de identidad
- Pasaportes
- Libros, artículos o publicaciones
- Contratos, actas de reunión, certificados laborales
- Recibos, facturas, formularios
- Constancias de estudio (sin otorgar título)
- Cualquier otro documento que no sea un diploma/título académico

SISTEMA DE NIVELES EN COLOMBIA (solo aplica si ES diploma):
- Técnico profesional (2 años): NO cumple requisito de posgrado
- Tecnólogo / Tecnología (3 años): NO cumple requisito de posgrado
- Pregrado universitario / Profesional (4-5 años): SÍ cumple
- Especialización, Maestría, Doctorado: SÍ cumple

TEXTO EXTRAÍDO POR OCR (puede estar fragmentado):
---
{ocr_text}
---

REGLAS IMPORTANTES:
- Si el texto NO pertenece a un diploma, pon es_diploma=false y cumple_requisito=false
- Si el texto es muy fragmentado y no es posible determinar si es un diploma, pon es_diploma=false con confianza baja
- Solo pon es_diploma=true si hay evidencia clara (universidad, título otorgado, graduado, rector/decano, etc.)
- Nunca asumas que es un diploma si el texto es genérico o ambiguo

Responde ÚNICAMENTE en formato JSON válido:
{{
  "es_diploma": true|false,
  "cumple_requisito": true|false,
  "nivel_detectado": "técnico profesional|tecnólogo|pregrado universitario|especialización|maestría|doctorado|no aplica|no identificado",
  "titulo_detectado": "título exacto o 'no aplica' si no es diploma o 'no identificado'",
  "programa_detectado": "nombre del programa o 'no aplica' si no es diploma o 'no identificado'",
  "razon": "explicación en 1-2 oraciones de por qué es o no es diploma y si cumple el requisito",
  "confianza": "alta|media|baja"
}}"""

    message = client.messages.create(
        model=MODEL,
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}],
    )

    result = _parse_json(message.content[0].text)

    # Doble verificación con keywords:
    # Si la IA dice que ES diploma pero keywords detectaron NO diploma → bloquear
    if result.get("es_diploma") and resultado_diploma_kw == "no_es_diploma":
        result["es_diploma"] = False
        result["cumple_requisito"] = False
        result["confianza"] = "media"
        result["razon"] = (
            "Se detectaron indicadores de documento no académico (cédula, libro u otro). "
            + result.get("razon", "")
        )

    # Si la IA dice que cumple nivel pero keywords detectaron nivel técnico → bloquear
    if result.get("cumple_requisito") and resultado_nivel_kw == "no_cumple":
        result["cumple_requisito"] = False
        result["confianza"] = "media"
        result["razon"] = (
            "Se detectaron términos asociados a nivel tecnológico o técnico. "
            + result.get("razon", "")
        )

    # Garantizar coherencia: si no es diploma, no puede cumplir requisito
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
            return json.loads(text[start : end + 1])
        # Fallback seguro: ante error de parseo, no bloquear — funcionario decide
        return {
            "es_diploma": True,
            "cumple_requisito": True,
            "nivel_detectado": "no identificado",
            "titulo_detectado": "no identificado",
            "programa_detectado": "no identificado",
            "razon": "No fue posible analizar el documento por limitaciones del texto extraído. El funcionario debe verificar manualmente.",
            "confianza": "baja",
        }
