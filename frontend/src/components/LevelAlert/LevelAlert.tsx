import type { Modulo0NivelAcademico } from "../../types";
import "./LevelAlert.scss";

interface LevelAlertProps {
  nivel: Modulo0NivelAcademico;
  recomendacion: string;
  tiempoTotal: number;
  onReset: () => void;
}

const CONFIANZA_LABEL = {
  alta: "Alta",
  media: "Media",
  baja: "Baja — verificar manualmente",
};

export default function LevelAlert({ nivel, recomendacion, tiempoTotal, onReset }: LevelAlertProps) {
  return (
    <div className="level-alert">
      {/* Hero de bloqueo */}
      <div className="level-alert__hero">
        <div className="level-alert__icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <line x1="4.93" y1="4.93" x2="19.07" y2="19.07" />
          </svg>
        </div>
        <div className="level-alert__hero-content">
          <span className="level-alert__label">Análisis detenido</span>
          <h2 className="level-alert__title">Requisito de nivel académico no cumplido</h2>
          <p className="level-alert__recommendation">{recomendacion}</p>
        </div>
      </div>

      {/* Detalle del nivel detectado */}
      <div className="level-alert__detail">
        <h3 className="level-alert__detail-title">Detalle del análisis de nivel</h3>

        <div className="level-alert__row">
          <span className="level-alert__row-label">Nivel detectado</span>
          <span className="level-alert__row-value level-alert__row-value--alert">
            {nivel.nivel_detectado}
          </span>
        </div>

        <div className="level-alert__row">
          <span className="level-alert__row-label">Título identificado</span>
          <span className="level-alert__row-value">{nivel.titulo_detectado}</span>
        </div>

        <div className="level-alert__row">
          <span className="level-alert__row-label">Programa identificado</span>
          <span className="level-alert__row-value">{nivel.programa_detectado}</span>
        </div>

        <div className="level-alert__row">
          <span className="level-alert__row-label">Confianza del análisis</span>
          <span className={`level-alert__row-value level-alert__badge level-alert__badge--${nivel.confianza}`}>
            {CONFIANZA_LABEL[nivel.confianza]}
          </span>
        </div>

        <div className="level-alert__reason">
          <span className="level-alert__reason-label">Justificación</span>
          <p className="level-alert__reason-text">{nivel.razon}</p>
        </div>
      </div>

      {/* Nota legal */}
      <div className="level-alert__legal">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
        <p>
          Según la <strong>Ley 30 de 1992</strong> y el <strong>Decreto 1330 de 2019</strong>,
          el acceso a programas de posgrado en Colombia requiere título de pregrado universitario.
          Títulos de nivel tecnológico o técnico profesional no cumplen este requisito para
          especializaciones universitarias, maestrías ni doctorados.
          {nivel.confianza === "baja" && (
            <span className="level-alert__low-confidence">
              {" "}La confianza del análisis es baja por limitaciones del OCR.
              Se recomienda verificar manualmente el nivel del título.
            </span>
          )}
        </p>
      </div>

      <div className="level-alert__footer">
        <span className="level-alert__time">
          Tiempo de análisis: {(tiempoTotal / 1000).toFixed(2)} s
        </span>
        <button className="level-alert__reset" onClick={onReset}>
          Analizar otro título
        </button>
      </div>
    </div>
  );
}
