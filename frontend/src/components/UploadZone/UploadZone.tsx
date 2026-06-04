import { useRef, useState, type DragEvent, type ChangeEvent } from "react";
import "./UploadZone.scss";

interface UploadZoneProps {
  onFileSelected: (file: File) => void;
  disabled?: boolean;
}

export default function UploadZone({ onFileSelected, disabled }: UploadZoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string>("");

  const handleFile = (file: File) => {
    const isImage = file.type.startsWith("image/");
    const isPdf = file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf");
    if (!isImage && !isPdf) {
      alert("Por favor selecciona una imagen (JPG, PNG) o un PDF.");
      return;
    }
    setFileName(file.name);
    setPreview(URL.createObjectURL(file));
    onFileSelected(file);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    if (disabled) return;
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  return (
    <div
      className={`upload-zone ${isDragging ? "upload-zone--dragging" : ""} ${
        disabled ? "upload-zone--disabled" : ""
      } ${preview ? "upload-zone--has-preview" : ""}`}
      onDragOver={(e) => {
        e.preventDefault();
        if (!disabled) setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      onClick={() => !disabled && inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept="image/*,application/pdf"
        onChange={handleChange}
        hidden
        disabled={disabled}
      />

      {preview ? (
        <div className="upload-zone__preview">
          <img src={preview} alt="Vista previa del título" />
          <div className="upload-zone__preview-overlay">
            <span className="upload-zone__filename">{fileName}</span>
            {!disabled && <span className="upload-zone__change">Clic para cambiar</span>}
          </div>
        </div>
      ) : (
        <div className="upload-zone__placeholder">
          <div className="upload-zone__icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
          </div>
          <p className="upload-zone__text">
            Arrastra el título escaneado o <span>haz clic para subirlo</span>
          </p>
          <p className="upload-zone__hint">Formatos aceptados: JPG, PNG, PDF · Imagen o documento del título físico</p>
        </div>
      )}
    </div>
  );
}
