import { useState } from "react";
import Header from "./components/Header/Header";
import UploadZone from "./components/UploadZone/UploadZone";
import ProcessingView from "./components/ProcessingView/ProcessingView";
import RiskReport from "./components/RiskReport/RiskReport";
import LevelAlert from "./components/LevelAlert/LevelAlert";
import { analizarTitulo } from "./services/api";
import type { ResultadoAnalisis, EstadoProceso } from "./types";
import "./App.scss";

export default function App() {
  const [estado, setEstado] = useState<EstadoProceso>("inicial");
  const [archivo, setArchivo] = useState<File | null>(null);
  const [resultado, setResultado] = useState<ResultadoAnalisis | null>(null);
  const [error, setError] = useState<string>("");

  const handleAnalizar = async () => {
    if (!archivo) return;
    setEstado("procesando");
    setError("");
    try {
      const res = await analizarTitulo(archivo);
      setResultado(res);
      if (res.estado === "bloqueado_por_nivel") {
        setEstado("bloqueado_por_nivel");
      } else {
        setEstado("completado");
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error desconocido");
      setEstado("error");
    }
  };

  const handleReset = () => {
    setEstado("inicial");
    setArchivo(null);
    setResultado(null);
    setError("");
  };

  return (
    <div className="app">
      <Header />
      <main className="app__main">
        <div className="app__container">
          {estado === "inicial" || estado === "error" ? (
            <>
              <div className="app__intro">
                <h2 className="app__intro-title">
                  Verificación de títulos académicos externos
                </h2>
                <p className="app__intro-text">
                  Sube la imagen escaneada de un título y el sistema ejecutará los cuatro
                  módulos del modelo para generar un reporte de riesgo de fraude.
                </p>
              </div>

              <UploadZone onFileSelected={setArchivo} />

              {error && (
                <div className="app__error">
                  <strong>Error:</strong> {error}
                  <span className="app__error-hint">
                    Verifica que el backend esté activo y que la URL de la API sea correcta.
                  </span>
                </div>
              )}

              <button
                className="app__analyze-btn"
                disabled={!archivo}
                onClick={handleAnalizar}
              >
                Analizar título
              </button>
            </>
          ) : estado === "procesando" ? (
            <ProcessingView />
          ) : (
            resultado && estado === "bloqueado_por_nivel" ? (
            <LevelAlert
              nivel={resultado.modulos.modulo_0_nivel_academico!}
              recomendacion={resultado.reporte.recomendacion}
              tiempoTotal={resultado.tiempo_total_ms}
              onReset={handleReset}
            />
          ) : (
            resultado && <RiskReport resultado={resultado} onReset={handleReset} />
          )
          )}
        </div>
      </main>
    </div>
  );
}
