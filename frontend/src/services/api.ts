// Servicio de comunicación con el backend
import type { ResultadoAnalisis } from "../types";

// URL del backend. En desarrollo local: http://localhost:8000
// Cuando uses Colab + ngrok, reemplaza por la URL pública de ngrok.
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * Envía la imagen del título al backend y devuelve el reporte completo
 * del análisis de los cuatro módulos.
 */
export async function analizarTitulo(archivo: File): Promise<ResultadoAnalisis> {
  const formData = new FormData();
  formData.append("archivo", archivo);

  const response = await fetch(`${API_URL}/api/analizar`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Error desconocido" }));
    throw new Error(error.detail || `Error ${response.status}`);
  }

  return response.json();
}

/**
 * Verifica que el backend esté activo.
 */
export async function verificarConexion(): Promise<boolean> {
  try {
    const response = await fetch(`${API_URL}/`);
    return response.ok;
  } catch {
    return false;
  }
}
