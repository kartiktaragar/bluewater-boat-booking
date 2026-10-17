
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { useAuth } from "./auth";
import Layout from "./components/Layout";
import Admin from "./pages/Admin";
import AuthPage from "./pages/Auth";
import BoatDetails from "./pages/BoatDetails";
import Boats from "./pages/Boats";
import Checkout from "./pages/Checkout";
import Home from "./pages/Home";
import MyBookings from "./pages/MyBookings";
import Profile from "./pages/Profile";
import Assistant from "./components/Assistant";

function ProtectedRoute({ children, admin = false }) {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) return <div className="page-loading">Loading your account…</div>;
  if (!user) return <Navigate to="/login" replace state={{ from: location }} />;
  if (admin && user.role !== "admin") return <Navigate to="/" replace />;

  return children;
}

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/boats" element={<Boats />} />
        <Route path="/boats/:id" element={<BoatDetails />} />
        <Route path="/login" element={<AuthPage mode="login" />} />
        <Route path="/signup" element={<AuthPage mode="signup" />} />
        <Route path="/checkout" element={<ProtectedRoute><Checkout /></ProtectedRoute>} />
        <Route path="/my-bookings" element={<ProtectedRoute><MyBookings /></ProtectedRoute>} />
        <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
        <Route path="/admin" element={<ProtectedRoute admin><Admin /></ProtectedRoute>} />
        <Route path="*" element={<section className="section-wrap py-32 text-center"><h1 className="heading-lg">Page not found</h1><a className="button-primary mt-6 inline-flex" href="/">Back to home</a></section>} />
      </Routes>

      {/* Floating AI assistant */}
      <Assistant />
    </Layout>
  );
}
