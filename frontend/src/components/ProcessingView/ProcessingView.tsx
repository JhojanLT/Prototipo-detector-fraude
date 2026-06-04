import { useEffect, useState } from "react";
import "./ProcessingView.scss";

const MODULOS = [
  { id: 1, nombre: "Preprocesamiento documental", desc: "Mejora de imagen y enderezado (LTHE)" },
  { id: 2, nombre: "Análisis visual", desc: "Detección de manipulación con CNN" },
  { id: 3, nombre: "Análisis textual", desc: "OCR + modelos Transformer" },
  { id: 4, nombre: "Fusión de decisiones", desc: "Consolidación y reporte de riesgo" },
];

export default function ProcessingView() {
  const [activeModule, setActiveModule] = useState(0);

  useEffect(() => {
    // Avanza visualmente por los módulos mientras el backend procesa
    const interval = setInterval(() => {
      setActiveModule((prev) => (prev < MODULOS.length - 1 ? prev + 1 : prev));
    }, 1800);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="processing-view">
      <div className="processing-view__spinner-wrap">
        <div className="processing-view__spinner" />
        <span className="processing-view__percent">Analizando</span>
      </div>

      <div className="processing-view__modules">
        {MODULOS.map((m, i) => (
          <div
            key={m.id}
            className={`processing-view__module ${
              i < activeModule
                ? "processing-view__module--done"
                : i === activeModule
                ? "processing-view__module--active"
                : ""
            }`}
          >
            <div className="processing-view__module-indicator">
              {i < activeModule ? (
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                  <polyline points="20 6 9 17 4 12" />
                </svg>
              ) : (
                <span>{m.id}</span>
              )}
            </div>
            <div className="processing-view__module-text">
              <span className="processing-view__module-name">{m.nombre}</span>
              <span className="processing-view__module-desc">{m.desc}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
