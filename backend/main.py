"""
Backend principal — Sistema de detección de fraude en títulos académicos
API REST construida con FastAPI que orquesta los módulos del modelo.

Flujo completo:
  imagen/PDF → Módulo 1 (preproc.) → OCR → Módulo 0 (nivel académico)
                                              ↓
                              ¿Es pregrado universitario?
                              ├── No  → alerta de nivel, detiene análisis
                              └── Sí  → Módulo 2 (visual) + Módulo 3 (textual)
                                              ↓
                                        Módulo 4 (fusión y reporte)

Universidad Libre, sede Bogotá — Prototipo de prueba de concepto.
"""

import time
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from modules import preprocessing, ocr, ai_analysis, level_check, pdf_converter

app = FastAPI(
    title="Sistema de Detección de Fraude en Títulos Académicos",
    description="Prototipo basado en IA — Universidad Libre, sede Bogotá",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {
        "status": "activo",
        "version": "2.0.0",
        "sistema": "Detección de fraude en títulos académicos",
        "institucion": "Universidad Libre, sede Bogotá",
        "modulos": [
            "Módulo 0 — Validación de nivel académico",
            "Módulo 1 — Preprocesamiento documental",
            "Módulo 2 — Análisis visual",
            "Módulo 3 — Análisis textual",
            "Módulo 4 — Fusión de decisiones",
        ],
        "formatos_aceptados": ["JPG", "PNG", "WEBP", "PDF"],
    }


@app.post("/api/analizar")
async def analizar_titulo(archivo: UploadFile = File(...)):
    """
    Endpoint principal. Acepta imagen (JPG/PNG/WEBP) o PDF.
    Ejecuta el flujo completo de módulos y devuelve el reporte.
    """
    filename = archivo.filename or ""
    content_type = archivo.content_type or ""

    # Validar tipo de archivo
    es_pdf = pdf_converter.is_pdf(content_type, filename)
    es_imagen = content_type.startswith("image/")

    if not es_pdf and not es_imagen:
        raise HTTPException(
            status_code=400,
            detail="Formato no soportado. Sube una imagen (JPG, PNG, WEBP) o un PDF.",
        )

    raw_bytes = await archivo.read()
    if len(raw_bytes) == 0:
        raise HTTPException(status_code=400, detail="El archivo está vacío.")

    resultado = {"modulos": {}}
    tiempo_inicio = time.time()

    try:
        # ── Conversión PDF → imagen (si aplica) ─────────────────────
        if es_pdf:
            try:
                image_bytes = pdf_converter.pdf_to_image_bytes(raw_bytes)
                resultado["conversion_pdf"] = {
                    "realizada": True,
                    "pagina": 1,
                    "mensaje": "PDF convertido a imagen (página 1) para análisis.",
                }
            except RuntimeError as e:
                raise HTTPException(status_code=422, detail=str(e))
        else:
            image_bytes = raw_bytes

        # ── MÓDULO 1: Preprocesamiento ──────────────────────────────
        t1 = time.time()
        imagen_procesada, meta_preproc = preprocessing.preprocess_document(image_bytes)
        png_procesado = preprocessing.to_png_bytes(imagen_procesada)
        meta_preproc["tiempo_ms"] = round((time.time() - t1) * 1000, 1)
        resultado["modulos"]["modulo_1_preprocesamiento"] = meta_preproc

        # ── OCR: Extracción de texto ─────────────────────────────────
        t_ocr = time.time()
        texto_extraido, meta_ocr = ocr.extract_text(imagen_procesada)
        meta_ocr["tiempo_ms"] = round((time.time() - t_ocr) * 1000, 1)
        meta_ocr["texto_extraido"] = texto_extraido
        resultado["modulos"]["modulo_3_ocr"] = meta_ocr

        # ── MÓDULO 0: Validación de nivel académico ──────────────────
        t0 = time.time()
        nivel = level_check.validate_academic_level(texto_extraido)
        nivel["tiempo_ms"] = round((time.time() - t0) * 1000, 1)
        resultado["modulos"]["modulo_0_nivel_academico"] = nivel

        # Si no cumple el requisito → detener análisis
        if not nivel.get("cumple_requisito", True):
            resultado["estado"] = "bloqueado_por_nivel"
            resultado["tiempo_total_ms"] = round((time.time() - tiempo_inicio) * 1000, 1)
            resultado["reporte"] = {
                "nivel_riesgo_global": "bloqueado",
                "puntuacion_confianza": 0,
                "elementos_verificados": [],
                "anomalias_detectadas": [
                    f"Nivel académico insuficiente: {nivel.get('nivel_detectado', 'no identificado')}",
                    f"Título detectado: {nivel.get('titulo_detectado', 'no identificado')}",
                ],
                "recomendacion": (
                    f"REQUISITO NO CUMPLIDO: El documento presentado corresponde a un título de "
                    f"{nivel.get('nivel_detectado', 'nivel no universitario')}. "
                    f"Para acceder a programas de posgrado en Colombia se requiere título de "
                    f"pregrado universitario (Ley 30 de 1992). "
                    f"Informar al aspirante y solicitar el título de pregrado correspondiente."
                ),
                "requiere_revision_humana": nivel.get("confianza") in ["baja", "media"],
                "bloqueado_por_nivel": True,
            }
            return JSONResponse(content=resultado)

        # ── MÓDULO 2: Análisis visual (IA) ──────────────────────────
        t2 = time.time()
        analisis_visual = ai_analysis.analyze_visual(png_procesado)
        analisis_visual["tiempo_ms"] = round((time.time() - t2) * 1000, 1)
        resultado["modulos"]["modulo_2_visual"] = analisis_visual

        # ── MÓDULO 3: Análisis textual (IA) ─────────────────────────
        t3 = time.time()
        analisis_textual = ai_analysis.analyze_text(texto_extraido)
        analisis_textual["tiempo_ms"] = round((time.time() - t3) * 1000, 1)
        resultado["modulos"]["modulo_3_textual"] = analisis_textual

        # ── MÓDULO 4: Fusión de decisiones (IA) ─────────────────────
        t4 = time.time()
        reporte_final = ai_analysis.fuse_decisions(analisis_visual, analisis_textual)
        reporte_final["tiempo_ms"] = round((time.time() - t4) * 1000, 1)
        reporte_final["bloqueado_por_nivel"] = False
        resultado["modulos"]["modulo_4_fusion"] = reporte_final

        resultado["reporte"] = reporte_final
        resultado["tiempo_total_ms"] = round((time.time() - tiempo_inicio) * 1000, 1)
        resultado["estado"] = "completado"

        return JSONResponse(content=resultado)

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error durante el análisis: {str(e)}",
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
