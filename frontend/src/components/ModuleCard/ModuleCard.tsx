import { useState, type ReactNode } from "react";
import "./ModuleCard.scss";

interface ModuleCardProps {
  numero: number;
  titulo: string;
  tiempoMs?: number;
  children: ReactNode;
  defaultOpen?: boolean;
}

export default function ModuleCard({
  numero,
  titulo,
  tiempoMs,
  children,
  defaultOpen = false,
}: ModuleCardProps) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className={`module-card ${open ? "module-card--open" : ""}`}>
      <button className="module-card__header" onClick={() => setOpen(!open)}>
        <div className="module-card__header-left">
          <span className="module-card__number">{numero}</span>
          <span className="module-card__title">{titulo}</span>
        </div>
        <div className="module-card__header-right">
          {tiempoMs !== undefined && (
            <span className="module-card__time">{tiempoMs} ms</span>
          )}
          <svg
            className="module-card__chevron"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </div>
      </button>
      {open && <div className="module-card__body">{children}</div>}
    </div>
  );
}
