import { ArrowLeft, MapPin, Users, Waves } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { api } from "../api";
import { ErrorMessage, LoadingState } from "../components/Feedback";

const dateToday = new Date().toISOString().slice(0, 10);

export default function BoatDetails() {
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const [boat, setBoat] = useState(null);
  const [dates, setDates] = useState({
    start_date: searchParams.get("start_date") || "",
    end_date: searchParams.get("end_date") || "",
    guests: searchParams.get("guests") || "2",
  });
  const [error, setError] = useState("");
  const [availability, setAvailability] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    api(`/boats/${id}`).then(setBoat).catch((err) => setError(err.message));
  }, [id]);

  async function checkDates(event) {
    event.preventDefault();
    setError("");
    setAvailability(null);
    try {
      const result = await api(`/boats/${id}/availability?start_date=${dates.start_date}&end_date=${dates.end_date}`);
      setAvailability(result.available);
      if (!result.available) setError("Those dates are no longer available. Try another range.");
    } catch (err) {
      setError(err.message);
    }
  }

  function continueBooking() {
    const params = new URLSearchParams({ boat_id: id, ...dates });
    navigate(`/checkout?${params}`);
  }

  if (!boat && !error) return <LoadingState label="Opening this boat…" />;
  if (!boat) return <section className="section-wrap py-16"><ErrorMessage>{error}</ErrorMessage><Link className="text-link mt-5" to="/boats"><ArrowLeft size={17} /> Back to boats</Link></section>;

  return (
    <section className="section-wrap py-8 sm:py-12">
      <Link to="/boats" className="back-link"><ArrowLeft size={16} /> All boats</Link>
      <div className="mt-6 grid gap-9 lg:grid-cols-[1.5fr_0.8fr]">
        <div>
          <div className="details-image"><img src={boat.image_url} alt={boat.name} /></div>
          <div className="mt-7 flex flex-wrap items-end justify-between gap-4">
            <div><span className="eyebrow"><Waves size={15} /> {boat.boat_type}</span><h1 className="heading-xl mt-2">{boat.name}</h1><p className="mt-2 flex items-center gap-1.5 text-muted"><MapPin size={16} /> {boat.location}</p></div>
            <div className="flex items-center gap-2 rounded-full bg-aqua px-4 py-2 text-sm font-semibold text-ocean"><Users size={17} /> Up to {boat.capacity} guests</div>
          </div>
          <div className="prose-copy mt-8"><h2>About this boat</h2><p>{boat.description}</p></div>
        </div>
        <aside className="booking-card">
          <p className="text-sm text-muted">A day on the water from</p><p className="mt-1 font-display text-3xl font-extrabold text-ink">${Number(boat.price_per_day).toLocaleString()} <span className="text-sm font-medium text-muted">/ day</span></p>
          <form onSubmit={checkDates} className="mt-6 space-y-4">
            <label className="form-label">Check in<input required type="date" min={dateToday} value={dates.start_date} onChange={(e) => { setDates({ ...dates, start_date: e.target.value }); setAvailability(null); }} /></label>
            <label className="form-label">Check out<input required type="date" min={dates.start_date || dateToday} value={dates.end_date} onChange={(e) => { setDates({ ...dates, end_date: e.target.value }); setAvailability(null); }} /></label>
            <label className="form-label">Guests<input required type="number" min="1" max={boat.capacity} value={dates.guests} onChange={(e) => setDates({ ...dates, guests: e.target.value })} /></label>
            <ErrorMessage>{error}</ErrorMessage>
            {availability === true ? <button type="button" className="button-primary w-full justify-center" onClick={continueBooking}>Continue to checkout</button> : <button className="button-primary w-full justify-center" type="submit">Check availability</button>}
          </form>
          <p className="mt-4 text-center text-xs text-muted">You won’t be charged until you confirm your booking.</p>
        </aside>
      </div>
    </section>
  );
}
