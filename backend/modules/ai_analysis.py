"""
Módulos 2, 3 (análisis) y 4 — Análisis inteligente con IA
Usa la API de Anthropic (Claude) para:
- Módulo 2: análisis visual del documento (visión por computadora)
- Módulo 3: análisis semántico del texto extraído por OCR
- Módulo 4: fusión de decisiones y generación del reporte de riesgo
"""

import base64
import json
from datetime import date
from anthropic import Anthropic

# El cliente toma la API key de la variable de entorno ANTHROPIC_API_KEY
client = Anthropic()

#MODEL = "claude-sonnet-4-20250514"

MODEL = "claude-haiku-4-5-20251001"


def analyze_visual(image_png_bytes: bytes) -> dict:
    """
    Módulo 2 — Análisis visual.
    Claude examina la imagen del documento buscando indicios de manipulación.
    """
    img_b64 = base64.standard_b64encode(image_png_bytes).decode("utf-8")

    prompt = """Eres un sistema experto en detección de fraude documental para una oficina de admisiones universitarias en Colombia. Analiza esta imagen de un título académico buscando indicios REALES de manipulación digital.

CONTEXTO CRÍTICO — estas características son NORMALES en títulos auténticos colombianos y NO deben reportarse como anomalías:
- Sellos con bordes difusos o aspecto de relieve: normal en diplomas físicos escaneados o fotografiados
- Firmas que parecen "irregulares" o "poco naturales": toda firma manuscrita se ve así en un scan
- Imagen borrosa, baja resolución o con ruido: normal en fotos de celular o escaneos básicos
- Texto decorativo o caligráfico difícil de leer: los diplomas colombianos usan estas fuentes
- Papel con textura, amarillento o con dobleces: normal en documentos físicos
- Sombras, reflejos o iluminación irregular: normal al fotografiar un documento físico
- Calidad general deficiente de la imagen: NO es señal de fraude por sí sola

SEÑALES REALES de manipulación digital que SÍ debes reportar:
1. Halos blancos o bordes artificiales alrededor de texto (indican elementos pegados digitalmente)
2. Diferencias drásticas de resolución ENTRE zonas del mismo documento (texto nítido sobre fondo pixelado o viceversa)
3. Inconsistencias de fuente DENTRO de un mismo campo de texto (parte del nombre en tipografía diferente)
4. Fondo de color diferente detrás de ciertos caracteres (indica texto superpuesto)
5. Elementos que claramente "flotan" sin integrarse al papel subyacente
6. Repetición exacta de patrones que deberían ser únicos (como una firma copiada y pegada)

IMPORTANTE: Sé muy conservador. Un diploma físico fotografiado o escaneado SIEMPRE tendrá imperfecciones. Solo marca anomalías cuando sean evidencia clara de edición digital, no de condiciones normales de digitalización. En caso de duda, no reportes como anomalía.

Responde ÚNICAMENTE en formato JSON válido, sin texto adicional:
{
  "elementos_verificados": ["elementos del documento que parecen auténticos"],
  "anomalias_visuales": ["SOLO anomalías claras de manipulación digital, no de calidad de imagen"],
  "nivel_sospecha_visual": "bajo|medio|alto",
  "observaciones": "explicación breve y objetiva del análisis"
}"""

    message = client.messages.create(
        model=MODEL,
        max_tokens=1500,
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

    return _parse_json_response(message.content[0].text)


def analyze_text(ocr_text: str) -> dict:
    """
    Módulo 3 — Análisis textual.
    Claude verifica la coherencia semántica del texto extraído del título.
    """
    fecha_hoy = date.today().strftime("%d de %B de %Y")
    prompt = f"""Eres un sistema experto en verificación de títulos académicos colombianos. Analiza el texto extraído por OCR de un título universitario presentado en admisiones a posgrado.

FECHA ACTUAL: {fecha_hoy}. Usa esta fecha como referencia para evaluar si las fechas del documento son coherentes. Una fecha de graduación anterior a hoy es válida. Solo marca anomalía si la fecha es posterior a la fecha actual o es claramente imposible (ej: año 1800, año 2100).

CONTEXTO CRÍTICO sobre la calidad del OCR:
El texto proviene de un OCR aplicado a una fotografía o escaneo de un diploma físico. Los diplomas colombianos usan fuentes caligráficas y decorativas que el OCR lee con dificultad. Por eso es NORMAL y NO es señal de fraude que:
- Aparezcan caracteres extraños, fragmentados o mal reconocidos
- Falten palabras o aparezcan incompletas
- El texto esté desordenado o con saltos de línea extraños
- Haya errores ortográficos introducidos por el OCR (no por el documento)
- No se identifiquen todos los campos (universidad, graduado, fecha, etc.)

Analiza el contenido semántico del texto, no los errores de OCR. Busca:
1. Si se puede identificar que es un título colombiano (universidad, programa académico, nombre del graduado, fecha, ciudad)
2. Inconsistencias SEMÁNTICAS graves: ej. una fecha imposible (año futuro), un programa que no existe, nombres de universidades inventadas
3. Combinaciones ilógicas: ej. título de medicina otorgado por una universidad de ingeniería
4. Si el texto tiene sentido como un diploma, aunque esté incompleto por limitaciones del OCR

NO reportes como anomalía:
- Campos no identificados por mala calidad del OCR
- Errores de escritura introducidos por el OCR
- Texto fragmentado o incompleto
- Ausencia de algunos elementos si el OCR no los pudo leer

TEXTO EXTRAÍDO POR OCR:
---
{ocr_text}
---

Responde ÚNICAMENTE en formato JSON válido, sin texto adicional:
{{
  "campos_identificados": {{"universidad": "...", "programa": "...", "graduado": "...", "fecha": "...", "ciudad": "..."}},
  "elementos_coherentes": ["elementos textuales que parecen correctos semánticamente"],
  "anomalias_textuales": ["SOLO inconsistencias semánticas graves, no errores de OCR"],
  "nivel_sospecha_textual": "bajo|medio|alto",
  "observaciones": "análisis objetivo del contenido, ignorando limitaciones del OCR"
}}

Si un campo no se puede identificar por limitaciones del OCR, usa "no identificado por calidad de imagen" como valor. Esto NO aumenta el nivel de sospecha."""

    message = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )

    return _parse_json_response(message.content[0].text)


def fuse_decisions(visual_result: dict, textual_result: dict) -> dict:
    """
    Módulo 4 — Fusión de decisiones y reporte.
    Claude combina los resultados de los módulos 2 y 3 mediante una valoración
    ponderada y genera el reporte final de riesgo para el funcionario de admisiones.
    """
    prompt = f"""Eres el módulo de fusión de decisiones de un sistema de detección de fraude en títulos académicos colombianos. Combinas los resultados del análisis visual (Módulo 2) y textual (Módulo 3) para generar un reporte final equilibrado.

RESULTADO DEL ANÁLISIS VISUAL:
{json.dumps(visual_result, ensure_ascii=False, indent=2)}

RESULTADO DEL ANÁLISIS TEXTUAL:
{json.dumps(textual_result, ensure_ascii=False, indent=2)}

REGLAS CRÍTICAS para la valoración ponderada:

RIESGO BAJO (confianza 70-100): cuando ambos módulos no detectan anomalías claras de manipulación digital. La baja calidad de imagen, el OCR fragmentado o la ausencia de campos por mala digitalización NO elevan el riesgo. Son documentos físicos normales.

RIESGO MEDIO (confianza 40-69): cuando hay algunas señales ambiguas que podrían explicarse tanto por manipulación como por condiciones normales de digitalización. Requiere revisión pero no rechazo inmediato.

RIESGO ALTO (confianza 0-39): ÚNICAMENTE cuando hay evidencia clara e inequívoca de manipulación digital: halos artificiales, inconsistencias de fuente dentro de campos de texto, diferencias drásticas de resolución entre zonas, o inconsistencias semánticas graves e inexplicables (fechas imposibles, universidades inexistentes).

IMPORTANTE: La baja calidad de imagen, sellos difusos, firmas irregulares y OCR fragmentado son características NORMALES de diplomas físicos colombianos escaneados o fotografiados. Por sí solos NO justifican riesgo alto ni medio.

En caso de duda, prefiere riesgo bajo o medio sobre riesgo alto. Es mejor pedir verificación adicional que rechazar un título auténtico.

Responde ÚNICAMENTE en formato JSON válido, sin texto adicional:
{{
  "nivel_riesgo_global": "bajo|medio|alto",
  "puntuacion_confianza": <0-100, confianza en la AUTENTICIDAD. Un diploma físico con buena coherencia semántica debe tener mínimo 60 aunque la imagen sea de baja calidad>,
  "elementos_verificados": ["elementos auténticos consolidados de ambos módulos"],
  "anomalias_detectadas": ["SOLO anomalías claras de manipulación, no de calidad de imagen"],
  "recomendacion": "recomendación objetiva y proporcionada para el funcionario de Admisiones",
  "requiere_revision_humana": true|false
}}

Recuerda: este sistema ASISTE la decisión humana. La recomendación debe ser proporcionada: no rechaces documentos solo por mala calidad de imagen."""

    message = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )

    return _parse_json_response(message.content[0].text)


def _parse_json_response(text: str) -> dict:
    """Extrae y parsea JSON de la respuesta del modelo de forma robusta."""
    text = text.strip()
    # Quitar fences de markdown si existen
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Intentar extraer el primer bloque {...}
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            return json.loads(text[start : end + 1])
        raise ValueError(f"No se pudo parsear la respuesta del modelo: {text[:200]}")