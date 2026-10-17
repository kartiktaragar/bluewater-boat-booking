import { CalendarDays, MapPin, XCircle } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { ErrorMessage, LoadingState, SuccessMessage } from "../components/Feedback";

export default function MyBookings() {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function load() {
    try {
      setBookings(await api("/bookings/mine"));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }
  useEffect(() => { load(); }, []);

  async function cancel(id) {
    setError("");
    setMessage("");
    try {
      await api(`/bookings/${id}/cancel`, { method: "POST" });
      setMessage("Your booking has been cancelled.");
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section className="section-wrap min-h-[70vh] py-12 sm:py-16">
      <span className="eyebrow"><CalendarDays size={15} /> YOUR TIME ON THE WATER</span><h1 className="heading-xl mt-3">My bookings.</h1><p className="mt-3 text-muted">All the good days you have coming up.</p>
      <ErrorMessage>{error}</ErrorMessage><SuccessMessage>{message}</SuccessMessage>
      {loading ? <LoadingState /> : bookings.length ? <div className="mt-8 space-y-4">{bookings.map((booking) => <article className="booking-row" key={booking.id}><img src={booking.boat.image_url} alt={booking.boat.name} /><div className="min-w-0 flex-1"><div className="flex flex-wrap items-center gap-2"><h2 className="font-display text-lg font-bold text-ink">{booking.boat.name}</h2><span className={`status-pill status-${booking.status}`}>{booking.status}</span></div><p className="mt-1 flex items-center gap-1 text-sm text-muted"><MapPin size={14} /> {booking.boat.location}</p><p className="mt-2 text-sm text-muted">{booking.start_date} — {booking.end_date} · ${Number(booking.total_price).toLocaleString()}</p><p className="mt-1 text-xs text-muted">Payment: {booking.payment?.status || "pending"}</p></div>{booking.status === "confirmed" && booking.payment?.status !== "succeeded" && <button className="button-outline text-sm" onClick={() => cancel(booking.id)}><XCircle size={15} /> Cancel</button>}</article>)}</div> : <div className="empty-state mt-10"><div className="empty-icon"><CalendarDays size={22} /></div><h2>Your next getaway is waiting.</h2><p>No bookings yet. Let’s change that.</p><Link to="/boats" className="button-primary mt-5">Explore boats</Link></div>}
    </section>
  );
}
