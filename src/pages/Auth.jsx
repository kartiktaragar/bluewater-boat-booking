import { Anchor, ArrowLeft, ArrowRight, Eye, EyeOff } from "lucide-react";
import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";
import { ErrorMessage } from "../components/Feedback";

export default function AuthPage({ mode }) {
  const signupMode = mode === "signup";
  const { login, signup } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ full_name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  async function submit(event) {
    event.preventDefault();
    setError("");
    setBusy(true);
    try {
      if (signupMode) await signup(form);
      else await login({ email: form.email, password: form.password });
      navigate(location.state?.from?.pathname || "/boats", { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="auth-shell">
      <div className="auth-photo"><div><span className="eyebrow eyebrow-light"><Anchor size={15} /> A DIFFERENT KIND OF GETAWAY</span><h2>Let the days<br />drift a little.</h2><p>Find the boat. Bring your people. We’ll see you out there.</p></div><span className="auth-photo-credit">A little further from ordinary.</span></div>
      <div className="auth-form-side">
        <Link to="/" className="back-link"><ArrowLeft size={16} /> Back to home</Link>
        <div className="auth-form-wrap">
          <span className="eyebrow">{signupMode ? "YOUR NEXT CHAPTER" : "GOOD TO HAVE YOU BACK"}</span>
          <h1 className="heading-lg mt-2">{signupMode ? "Make waves." : "Welcome back."}</h1>
          <p className="mt-2 text-sm text-muted">{signupMode ? "Create an account and start planning your escape." : "Log in and get back to the good part."}</p>
          <ErrorMessage>{error}</ErrorMessage>
          <form onSubmit={submit} className="mt-7 space-y-4">
            {signupMode && <label className="form-label">Full name<input required minLength="2" maxLength="120" autoComplete="name" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} placeholder="Your name" /></label>}
            <label className="form-label">Email address<input required type="email" autoComplete="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} placeholder="you@example.com" /></label>
            <label className="form-label">Password<span className="password-input"><input required minLength={signupMode ? 8 : undefined} type={showPassword ? "text" : "password"} autoComplete={signupMode ? "new-password" : "current-password"} value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} placeholder={signupMode ? "At least 8 characters" : "Your password"} /><button type="button" onClick={() => setShowPassword(!showPassword)} aria-label={showPassword ? "Hide password" : "Show password"}>{showPassword ? <EyeOff size={17} /> : <Eye size={17} />}</button></span></label>
            <button type="submit" disabled={busy} className="button-primary w-full justify-center">{busy ? "One moment…" : signupMode ? "Create account" : "Log in"} {!busy && <ArrowRight size={17} />}</button>
          </form>
          <p className="mt-6 text-center text-sm text-muted">{signupMode ? "Already have an account?" : "New to Bluewater?"} <Link className="font-bold text-ocean hover:underline" to={signupMode ? "/login" : "/signup"}>{signupMode ? "Log in" : "Create an account"}</Link></p>
        </div>
      </div>
    </section>
  );
}
