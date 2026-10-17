export function ErrorMessage({ children }) {
  if (!children) return null;
  return <div role="alert" className="notice notice-error">{children}</div>;
}

export function SuccessMessage({ children }) {
  if (!children) return null;
  return <div role="status" className="notice notice-success">{children}</div>;
}

export function LoadingState({ label = "Loading..." }) {
  return <div className="py-16 text-center text-sm text-muted">{label}</div>;
}
