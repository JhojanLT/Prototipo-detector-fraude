import "./Header.scss";

export default function Header() {
  return (
    <header className="app-header">
      <div className="app-header__brand">
        <div className="app-header__logo">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 2L3 6v6c0 5.5 3.8 10.7 9 12 5.2-1.3 9-6.5 9-12V6l-9-4z" />
            <path d="M9 12l2 2 4-4" />
          </svg>
        </div>
        <div className="app-header__titles">
          <h1 className="app-header__title">VeriTítulo</h1>
          <p className="app-header__subtitle">
            Detección de fraude en títulos académicos · Prototipo
          </p>
        </div>
      </div>
      <div className="app-header__institution">
        <span className="app-header__institution-name">Universidad Libre</span>
        <span className="app-header__institution-campus">Sede Bogotá</span>
      </div>
    </header>
  );
}
