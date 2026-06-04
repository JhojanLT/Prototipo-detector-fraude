# VeriTítulo — Sistema de Detección de Fraude en Títulos Académicos

Prototipo de prueba de concepto basado en Inteligencia Artificial para la verificación de títulos académicos externos en procesos de admisión a posgrado.

**Universidad Libre, sede Bogotá** · Facultad de Ingeniería

---

## ¿Qué hace?

Recibe la imagen escaneada de un título académico y ejecuta los cuatro módulos del modelo conceptual para generar un reporte de riesgo de fraude:

1. **Módulo 1 — Preprocesamiento documental** (OpenCV): mejora de imagen, enderezado, reducción de ruido y realce de contraste tipo LTHE.
2. **Módulo 2 — Análisis visual** (IA): detección de inconsistencias tipográficas, sellos y firmas alteradas.
3. **Módulo 3 — Análisis textual** (Tesseract OCR + IA): extracción de texto y verificación semántica de coherencia.
4. **Módulo 4 — Fusión de decisiones** (IA): consolida los análisis y produce un nivel de riesgo y recomendación.

> **Importante:** este prototipo no reemplaza la decisión humana. Asiste al funcionario de Admisiones y Registro con información objetiva y trazable. Los modelos no están entrenados con títulos colombianos reales, por lo que la precisión es ilustrativa, no productiva.

---

## Estructura del proyecto

```
deteccion-fraude-titulos/
├── frontend/          App React + TypeScript + SCSS + Tailwind (Vite)
├── backend/           API FastAPI con los cuatro módulos (Python)
├── colab/             Notebook para correr el backend en Google Colab
└── README.md
```

Frontend y backend son **proyectos independientes** que se comunican por HTTP.

---

## Cómo ejecutarlo

### Opción A — Todo local

**Backend:**
```bash
cd backend
pip install -r requirements.txt
# Configura tu API key de Anthropic:
export ANTHROPIC_API_KEY="sk-ant-..."
# Asegúrate de tener Tesseract instalado con español:
#   Ubuntu/Debian: sudo apt-get install tesseract-ocr tesseract-ocr-spa
#   Mac: brew install tesseract tesseract-lang
python main.py
```
El backend queda en `http://localhost:8000`.

**Frontend:**
```bash
cd frontend
npm install
cp .env.example .env   # VITE_API_URL ya apunta a localhost:8000
npm run dev
```
Abre `http://localhost:5173`.

---

### Opción B — Backend en Google Colab (recomendado para demos)

1. Abre `colab/backend_colab.ipynb` en Google Colab.
2. Ejecuta las celdas en orden:
   - Celda 1: instala dependencias
   - Celda 2: pega tu API key de Anthropic
   - Celda 3: sube los archivos del `backend/` (o clona el repo)
   - Celda 4: pega tu authtoken de ngrok → genera una **URL pública**
   - Celda 5: arranca el servidor
3. Copia la URL pública de ngrok.
4. En `frontend/.env`, pon esa URL en `VITE_API_URL`.
5. Corre el frontend con `npm run dev`.

---

## Requisitos previos

- **Node.js** 18+ (frontend)
- **Python** 3.10+ (backend)
- **Tesseract OCR** con idioma español (`spa`)
- **API key de Anthropic** — https://console.anthropic.com/
- **Cuenta de ngrok** (solo para Opción B) — https://ngrok.com/

---

## Stack técnico

| Capa | Tecnologías |
|------|-------------|
| Frontend | React 18, TypeScript, SCSS, Tailwind CSS, Vite |
| Backend | FastAPI, OpenCV, Tesseract (pytesseract), Anthropic SDK |
| IA | Claude (análisis visual, textual y fusión) |
| Despliegue demo | Google Colab + ngrok |

---

## Limitaciones del prototipo

- Los modelos de IA no están entrenados (fine-tuning) con títulos colombianos reales.
- No se conecta a bases de datos institucionales de la Universidad Libre.
- Google Colab + ngrok son temporales (la URL cambia al reiniciar la sesión).
- Es una demostración de viabilidad, alineada con el trabajo futuro descrito en el artículo.

---

## Trabajo futuro

- Recopilar muestras documentales reales con Admisiones y Registro.
- Crear un conjunto de títulos falsificados sintéticos para entrenamiento.
- Hacer fine-tuning de TrOCR (módulo 3) y de una CNN como ResNet/EfficientNet (módulo 2).
- Migrar el backend a un servicio permanente (Railway, Render o Hugging Face Spaces).
- Validación institucional bajo la Ley 1581 de 2012 de protección de datos.
