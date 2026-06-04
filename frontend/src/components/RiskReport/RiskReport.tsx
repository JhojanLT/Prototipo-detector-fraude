import type { ResultadoAnalisis, NivelRiesgo } from "../../types";
import ModuleCard from "../ModuleCard/ModuleCard";
import "./RiskReport.scss";

interface RiskReportProps {
  resultado: ResultadoAnalisis;
  onReset: () => void;
}

const RIESGO_LABEL: Record<NivelRiesgo, string> = {
  bajo: "Riesgo Bajo",
  medio: "Riesgo Medio",
  alto: "Riesgo Alto",
  bloqueado: "Bloqueado",
};

export default function RiskReport({ resultado, onReset }: RiskReportProps) {
  const { reporte, modulos } = resultado;
  const m0 = modulos.modulo_0_nivel_academico;
  const m1 = modulos.modulo_1_preprocesamiento;
  const mOcr = modulos.modulo_3_ocr;
  const m2 = modulos.modulo_2_visual;
  const m3 = modulos.modulo_3_textual;

  return (
    <div className="risk-report">
      {/* Tarjeta principal de riesgo */}
      <div className={`risk-report__hero risk-report__hero--${reporte.nivel_riesgo_global}`}>
        <div className="risk-report__hero-left">
          <span className="risk-report__hero-label">Resultado del análisis</span>
          <h2 className="risk-report__hero-risk">
            {RIESGO_LABEL[reporte.nivel_riesgo_global]}
          </h2>
          <p className="risk-report__hero-recommendation">{reporte.recomendacion}</p>
          {reporte.requiere_revision_humana && (
            <div className="risk-report__human-flag">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 9v4M12 17h.01M10.3 3.9L1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z" />
              </svg>
              Requiere revisión humana
            </div>
          )}
        </div>
        <div className="risk-report__gauge">
          <svg viewBox="0 0 120 120">
            <circle className="risk-report__gauge-bg" cx="60" cy="60" r="52" />
            <circle
              className="risk-report__gauge-fill"
              cx="60"
              cy="60"
              r="52"
              style={{
                strokeDashoffset: 327 - (327 * reporte.puntuacion_confianza) / 100,
              }}
            />
          </svg>
          <div className="risk-report__gauge-text">
            <span className="risk-report__gauge-value">{reporte.puntuacion_confianza}</span>
            <span className="risk-report__gauge-unit">% confianza</span>
          </div>
        </div>
      </div>

      {/* Resumen de verificados y anomalías */}
      <div className="risk-report__summary">
        <div className="risk-report__summary-col">
          <h3 className="risk-report__summary-title risk-report__summary-title--ok">
            Elementos verificados
          </h3>
          <ul className="module-detail__list module-detail__list--ok">
            {reporte.elementos_verificados.length > 0 ? (
              reporte.elementos_verificados.map((e, i) => <li key={i}>{e}</li>)
            ) : (
              <li>Sin elementos verificados</li>
            )}
          </ul>
        </div>
        <div className="risk-report__summary-col">
          <h3 className="risk-report__summary-title risk-report__summary-title--alert">
            Anomalías detectadas
          </h3>
          <ul className="module-detail__list module-detail__list--alert">
            {reporte.anomalias_detectadas.length > 0 ? (
              reporte.anomalias_detectadas.map((a, i) => <li key={i}>{a}</li>)
            ) : (
              <li>No se detectaron anomalías</li>
            )}
          </ul>
        </div>
      </div>

      {/* Detalle por módulo */}
      <h3 className="risk-report__modules-heading">Detalle por módulo</h3>

      {m0 && (
        <ModuleCard numero={0} titulo="Validación de nivel académico" tiempoMs={m0.tiempo_ms} defaultOpen>
          <div className="module-detail__row">
            <span className="module-detail__label">Cumple requisito</span>
            <span className="module-detail__value" style={{ color: m0.cumple_requisito ? "var(--color-ok, #10b981)" : "var(--color-alert, #ef4444)" }}>
              {m0.cumple_requisito ? "✓ Sí" : "✗ No"}
            </span>
          </div>
          <div className="module-detail__row">
            <span className="module-detail__label">Nivel detectado</span>
            <span className="module-detail__value">{m0.nivel_detectado}</span>
          </div>
          <div className="module-detail__row">
            <span className="module-detail__label">Título</span>
            <span className="module-detail__value">{m0.titulo_detectado}</span>
          </div>
          <div className="module-detail__row">
            <span className="module-detail__label">Programa</span>
            <span className="module-detail__value">{m0.programa_detectado}</span>
          </div>
          <div className="module-detail__row">
            <span className="module-detail__label">Confianza</span>
            <span className="module-detail__value">{m0.confianza}</span>
          </div>
          <p className="module-detail__observation">{m0.razon}</p>
        </ModuleCard>
      )}

      <ModuleCard numero={1} titulo="Preprocesamiento documental" tiempoMs={m1.tiempo_ms}>
        <div className="module-detail__row">
          <span className="module-detail__label">Dimensiones originales</span>
          <span className="module-detail__value">{m1.dimensiones_originales}</span>
        </div>
        <p className="module-detail__section-title">Pasos aplicados</p>
        <ul className="module-detail__list module-detail__list--ok">
          {m1.pasos_aplicados.map((p, i) => (
            <li key={i}>{p}</li>
          ))}
        </ul>
      </ModuleCard>

      {m2 && <ModuleCard numero={2} titulo="Análisis visual" tiempoMs={m2.tiempo_ms}>
        <div className="module-detail__row">
          <span className="module-detail__label">Nivel de sospecha visual</span>
          <span className="module-detail__value">{m2!.nivel_sospecha_visual}</span>
        </div>
        {m2!.elementos_verificados.length > 0 && (
          <>
            <p className="module-detail__section-title">Elementos auténticos</p>
            <ul className="module-detail__list module-detail__list--ok">
              {m2!.elementos_verificados.map((e, i) => (
                <li key={i}>{e}</li>
              ))}
            </ul>
          </>
        )}
        {m2!.anomalias_visuales.length > 0 && (
          <>
            <p className="module-detail__section-title">Anomalías visuales</p>
            <ul className="module-detail__list module-detail__list--alert">
              {m2!.anomalias_visuales.map((a, i) => (
                <li key={i}>{a}</li>
              ))}
            </ul>
          </>
        )}
        <p className="module-detail__observation">{m2!.observaciones}</p>
      </ModuleCard>}

      {m3 && <ModuleCard numero={3} titulo="Análisis textual (OCR + Transformer)" tiempoMs={m3.tiempo_ms}>
        <div className="module-detail__row">
          <span className="module-detail__label">Confianza OCR</span>
          <span className="module-detail__value">{mOcr.confianza_promedio_ocr}</span>
        </div>
        <div className="module-detail__row">
          <span className="module-detail__label">Palabras detectadas</span>
          <span className="module-detail__value">{mOcr.palabras_detectadas}</span>
        </div>
        <p className="module-detail__section-title">Campos identificados</p>
        {Object.entries(m3!.campos_identificados).map(([k, v]) => (
          <div className="module-detail__row" key={k}>
            <span className="module-detail__label">{k}</span>
            <span className="module-detail__value">{v || "no identificado"}</span>
          </div>
        ))}
        {m3!.anomalias_textuales.length > 0 && (
          <>
            <p className="module-detail__section-title">Anomalías textuales</p>
            <ul className="module-detail__list module-detail__list--alert">
              {m3!.anomalias_textuales.map((a, i) => (
                <li key={i}>{a}</li>
              ))}
            </ul>
          </>
        )}
        <p className="module-detail__section-title">Texto extraído (OCR)</p>
        <pre className="module-detail__ocr-text">{mOcr.texto_extraido}</pre>
        <p className="module-detail__observation">{m3!.observaciones}</p>
      </ModuleCard>}

      <div className="risk-report__footer">
        <span className="risk-report__total-time">
          Tiempo total de análisis: {(resultado.tiempo_total_ms / 1000).toFixed(2)} s
        </span>
        <button className="risk-report__reset" onClick={onReset}>
          Analizar otro título
        </button>
      </div>

      <p className="risk-report__disclaimer">
        Este sistema es un prototipo de prueba de concepto. No reemplaza la decisión humana:
        asiste al funcionario de Admisiones y Registro con información objetiva y trazable.
      </p>
    </div>
  );
}
