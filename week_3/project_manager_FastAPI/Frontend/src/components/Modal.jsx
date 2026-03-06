export default function Modal({ open, title, onClose, children }) {
  if (!open) return null;

  return (
    <div className="modalOverlay" onClick={onClose} role="presentation">
      <div
        className="modalCard"
        onClick={(event) => event.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-label={title}
      >
        <div className="modalHeader">
          <h3 className="modalTitle">{title}</h3>
          <button className="btn" type="button" onClick={onClose}>
            إغلاق
          </button>
        </div>
        <div className="modalBody">{children}</div>
      </div>
    </div>
  );
}
