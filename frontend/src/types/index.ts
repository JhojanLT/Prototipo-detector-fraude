// Tipos del sistema de detección de fraude en títulos académicos v2

export type NivelRiesgo = "bajo" | "medio" | "alto" | "bloqueado";
export type EstadoProceso = "inicial" | "procesando" | "completado" | "bloqueado_por_nivel" | "bloqueado_por_tipo" | "error";
export type ConfianzaNivel = "alta" | "media" | "baja";

export interface Modulo0NivelAcademico {
  es_diploma: boolean;
  cumple_requisito: boolean;
  nivel_detectado: string;
  titulo_detectado: string;
  programa_detectado: string;
  razon: string;
  confianza: ConfianzaNivel;
  tiempo_ms: number;
}

export interface Modulo1Preprocesamiento {
  dimensiones_originales: string;
  pasos_aplicados: string[];
  modulo: string;
  tiempo_ms: number;
}

export interface Modulo3OCR {
  confianza_promedio_ocr: string;
  palabras_detectadas: number;
  motor: string;
  texto_extraido: string;
  modulo: string;
  tiempo_ms: number;
}

export interface Modulo2Visual {
  elementos_verificados: string[];
  anomalias_visuales: string[];
  nivel_sospecha_visual: "bajo" | "medio" | "alto";
  observaciones: string;
  tiempo_ms: number;
}

export interface CamposIdentificados {
  universidad?: string;
  programa?: string;
  graduado?: string;
  fecha?: string;
  ciudad?: string;
}

export interface Modulo3Textual {
  campos_identificados: CamposIdentificados;
  elementos_coherentes: string[];
  anomalias_textuales: string[];
  nivel_sospecha_textual: "bajo" | "medio" | "alto";
  observaciones: string;
  tiempo_ms: number;
}

export interface ReporteFinal {
  nivel_riesgo_global: NivelRiesgo;
  puntuacion_confianza: number;
  elementos_verificados: string[];
  anomalias_detectadas: string[];
  recomendacion: string;
  requiere_revision_humana: boolean;
  bloqueado_por_nivel?: boolean;
  bloqueado_por_tipo?: boolean;
  tiempo_ms?: number;
}

export interface ConversionPDF {
  realizada: boolean;
  pagina: number;
  mensaje: string;
}

export interface ResultadoAnalisis {
  estado: string;
  tiempo_total_ms: number;
  reporte: ReporteFinal;
  conversion_pdf?: ConversionPDF;
  modulos: {
    modulo_0_nivel_academico?: Modulo0NivelAcademico;
    modulo_1_preprocesamiento: Modulo1Preprocesamiento;
    modulo_3_ocr: Modulo3OCR;
    modulo_2_visual?: Modulo2Visual;
    modulo_3_textual?: Modulo3Textual;
    modulo_4_fusion?: ReporteFinal;
  };
}
