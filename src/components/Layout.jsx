import { useState } from "react";
import { Anchor, Menu, X } from "lucide-react";
import { Link, NavLink } from "react-router-dom";
import { useAuth } from "../auth";

export default function Layout({ children }) {
  const { user, logout } = useAuth();
  const [open, setOpen] = useState(false);
  const close = () => setOpen(false);
  const linkClass = ({ isActive }) => `nav-link ${isActive ? "nav-link-active" : ""}`;

  return (
    <div className="min-h-screen">
      <header className="site-header">
        <div className="section-wrap flex h-[76px] items-center justify-between">
          <Link to="/" className="brand" onClick={close}><span className="brand-mark"><Anchor size={19} /></span>bluewater<span className="brand-period">.</span></Link>
          <button className="mobile-menu-button" aria-label="Toggle navigation" onClick={() => setOpen(!open)}>{open ? <X /> : <Menu />}</button>
          <nav className={`nav-items ${open ? "nav-items-open" : ""}`}>
            <NavLink to="/boats" className={linkClass} onClick={close}>Explore ships</NavLink>
            {user ? (
              <>
                <NavLink to="/my-bookings" className={linkClass} onClick={close}>My bookings</NavLink>
                {user.role === "admin" && <NavLink to="/admin" className={linkClass} onClick={close}>Dashboard</NavLink>}
                <NavLink to="/profile" className={linkClass} onClick={close}>{user.full_name.split(" ")[0]}</NavLink>
                <button className="button-outline !py-2.5" onClick={() => { logout(); close(); }}>Log out</button>
              </>
            ) : (
              <>
                <NavLink to="/login" className={linkClass} onClick={close}>Log in</NavLink>
                <Link to="/signup" className="button-primary !py-2.5" onClick={close}>Get started</Link>
              </>
            )}
          </nav>
        </div>
      </header>
      <main>{children}</main>
      <footer className="site-footer">
        <div className="section-wrap flex flex-col gap-8 py-10 sm:flex-row sm:items-center sm:justify-between">
          <Link to="/" className="brand text-white"><span className="brand-mark"><Anchor size={18} /></span>bluewater<span className="brand-period">.</span></Link>
          <p className="text-sm text-white/60">Make room for the good kind of nowhere.</p>
          <p className="text-xs text-white/45">© {new Date().getFullYear()} Bluewater Boat Co.</p>
        </div>
      </footer>
    </div>
  );
}
