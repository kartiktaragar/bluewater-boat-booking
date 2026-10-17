import { BarChart3, Plus, Ship, Users } from "lucide-react";
import { useEffect, useState } from "react";
import { api } from "../api";
import { ErrorMessage, SuccessMessage } from "../components/Feedback";

const emptyBoat = {
  name: "", location: "", description: "", boat_type: "Sailing",
  capacity: 6, price_per_day: "", image_url: "", is_active: true,
};

export default function Admin() {
  const [stats, setStats] = useState(null);
  const [bookings, setBookings] = useState([]);
  const [form, setForm] = useState(emptyBoat);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  async function load() {
    try {
      const [summary, allBookings] = await Promise.all([api("/admin/stats"), api("/admin/bookings")]);
      setStats(summary);
      setBookings(allBookings);
    } catch (err) {
      setError(err.message);
    }
  }
  useEffect(() => { load(); }, []);

  async function createBoat(event) {
    event.preventDefault();
    setError("");
    setMessage("");
    setBusy(true);
    try {
      await api("/admin/boats", { method: "POST", body: JSON.stringify({ ...form, capacity: Number(form.capacity), price_per_day: Number(form.price_per_day) }) });
      setForm(emptyBoat);
      setMessage("Boat listing created.");
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function updateBooking(id, key, value) {
    setError("");
    try {
      const queryName = key === "status" ? "booking_status" : "payment_status";
      if (key === "payment") {
        await api(`/admin/bookings/${id}/refund`, { method: "POST" });
      } else {
        await api(`/admin/bookings/${id}/status?${queryName}=${encodeURIComponent(value)}`, { method: "PATCH" });
      }
      setMessage("Booking updated.");
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section className="section-wrap min-h-[70vh] py-12 sm:py-16">
      <span className="eyebrow"><BarChart3 size={15} /> CAPTAIN’S LOG</span><h1 className="heading-xl mt-3">Admin dashboard.</h1><p className="mt-3 text-muted">A clear view of the fleet and the folks heading out to sea.</p>
      <ErrorMessage>{error}</ErrorMessage><SuccessMessage>{message}</SuccessMessage>
      <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard icon={<Ship />} label="Active boats" value={stats?.boats ?? "—"} />
        <StatCard icon={<BarChart3 />} label="Total bookings" value={stats?.bookings ?? "—"} />
        <StatCard icon={<Users />} label="Customers" value={stats?.customers ?? "—"} />
        <StatCard icon={<span className="font-bold">$</span>} label="Paid revenue" value={stats ? `$${Number(stats.revenue).toLocaleString()}` : "—"} />
      </div>
      <div className="mt-10 grid gap-8 xl:grid-cols-[0.8fr_1.2fr]">
        <form className="panel-card p-6" onSubmit={createBoat}>
          <h2 className="font-display text-xl font-bold text-ink"><Plus size={19} className="mr-1 inline text-ocean" /> Add a boat listing</h2>
          <div className="mt-5 grid gap-4 sm:grid-cols-2">
            <label className="form-label">Boat name<input required minLength="2" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></label>
            <label className="form-label">Location<input required value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} /></label>
            <label className="form-label">Type<input required value={form.boat_type} onChange={(e) => setForm({ ...form, boat_type: e.target.value })} /></label>
            <label className="form-label">Capacity<input required type="number" min="1" value={form.capacity} onChange={(e) => setForm({ ...form, capacity: e.target.value })} /></label>
            <label className="form-label">Price per day<input required type="number" min="0.01" step="0.01" value={form.price_per_day} onChange={(e) => setForm({ ...form, price_per_day: e.target.value })} /></label>
            <label className="form-label">Image URL<input required type="url" value={form.image_url} onChange={(e) => setForm({ ...form, image_url: e.target.value })} /></label>
            <label className="form-label sm:col-span-2">Description<textarea required minLength="10" rows="3" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></label>
          </div>
          <button className="button-primary mt-5" disabled={busy}>{busy ? "Saving…" : "Create listing"} <Plus size={16} /></button>
        </form>
        <div className="panel-card overflow-hidden">
          <div className="border-b border-slate-100 px-6 py-5"><h2 className="font-display text-xl font-bold text-ink">Recent bookings</h2><p className="mt-1 text-sm text-muted">Manage reservation and payment status.</p></div>
          <div className="overflow-x-auto"><table className="admin-table"><thead><tr><th>Guest / boat</th><th>Dates</th><th>Booking</th><th>Payment</th></tr></thead><tbody>
            {bookings.map((item) => <tr key={item.id}><td><strong>{item.boat.name}</strong><small>{item.user_id} · ${Number(item.total_price).toLocaleString()}</small></td><td>{item.start_date}<small>to {item.end_date}</small></td><td><select aria-label={`Booking ${item.id} status`} value={item.status} onChange={(e) => updateBooking(item.id, "status", e.target.value)}><option value="confirmed">Confirmed</option><option value="cancelled">Cancelled</option><option value="completed">Completed</option></select></td><td><span className={`status-pill ${item.payment?.status === "succeeded" ? "" : "status-cancelled"}`}>{item.payment?.status || "pending"}</span>{item.payment?.status === "succeeded" && <button className="mt-2 block text-xs font-bold text-ocean hover:underline" onClick={() => updateBooking(item.id, "payment", "refunded")}>Request refund</button>}<small>{item.payment?.provider || "—"}</small></td></tr>)}
            {!bookings.length && <tr><td colSpan="4" className="py-10 text-center text-muted">No bookings just yet.</td></tr>}
          </tbody></table></div>
        </div>
      </div>
    </section>
  );
}

function StatCard({ icon, label, value }) {
  return <article className="stat-card"><div className="stat-icon">{icon}</div><p className="mt-4 text-sm text-muted">{label}</p><p className="mt-1 font-display text-2xl font-extrabold text-ink">{value}</p></article>;
}
