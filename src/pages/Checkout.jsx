import { Elements, PaymentElement, useElements, useStripe } from "@stripe/react-stripe-js";
import { loadStripe } from "@stripe/stripe-js";
import { ArrowLeft, Check, LockKeyhole, Waves } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api } from "../api";
import { ErrorMessage, SuccessMessage } from "../components/Feedback";

function CardPayment({ bookingId, onPaid, onError }) {
  const stripe = useStripe();
  const elements = useElements();
  const [busy, setBusy] = useState(false);

  async function submit(event) {
    event.preventDefault();
    if (!stripe || !elements) return;
    setBusy(true);
    const result = await stripe.confirmPayment({
      elements,
      confirmParams: { return_url: `${window.location.origin}/my-bookings` },
      redirect: "if_required",
    });
    if (result.error) onError(result.error.message || "Payment could not be completed.");
    else onPaid();
    setBusy(false);
  }

  return <form onSubmit={submit} className="mt-5 space-y-5"><PaymentElement /><button className="button-primary w-full justify-center" disabled={!stripe || busy}>{busy ? "Processing…" : `Pay securely`} <LockKeyhole size={16} /></button></form>;
}

export default function Checkout() {
  const [params] = useSearchParams();
  const [boat, setBoat] = useState(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [booking, setBooking] = useState(null);
  const [payment, setPayment] = useState(null);
  const [busy, setBusy] = useState(false);
  const [paymentConfig, setPaymentConfig] = useState(null);
  const stripePromise = useMemo(() => payment?.publishable_key ? loadStripe(payment.publishable_key) : null, [payment?.publishable_key]);

  const bookingInput = {
    boat_id: Number(params.get("boat_id")),
    start_date: params.get("start_date"),
    end_date: params.get("end_date"),
    guests: Number(params.get("guests") || 1),
  };

  useEffect(() => {
    if (!bookingInput.boat_id || !bookingInput.start_date || !bookingInput.end_date) {
      setError("Choose a boat and dates before checking out.");
      return;
    }
    api(`/boats/${bookingInput.boat_id}`)
  .then((boatData) => {
    setBoat(boatData);
  })
  .catch((err) => {
    setError(`Could not load boat: ${err.message}`);
  });

api("/payments/config")
  .then((config) => {
    setPaymentConfig(config);
  })
  .catch(() => {
    // Continue without online card payments.
    setPaymentConfig({ enabled: false });
  });
  // Checkout details are read from the current URL on entry.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function confirmBooking() {
    setBusy(true);
    setError("");
    try {
      const created = await api("/bookings", { method: "POST", body: JSON.stringify(bookingInput) });
      setBooking(created);
      if (paymentConfig?.enabled) {
        const intent = await api(`/payments/bookings/${created.id}/intent`, { method: "POST" });
        setPayment(intent);
      } else {
        setMessage("Your booking is confirmed. Card payments aren’t enabled right now; payment remains pending.");
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  const nights = bookingInput.start_date && bookingInput.end_date
    ? Math.max(0, (new Date(`${bookingInput.end_date}T00:00:00`) - new Date(`${bookingInput.start_date}T00:00:00`)) / 86400000)
    : 0;

  return (
    <section className="section-wrap min-h-[70vh] py-10 sm:py-14">
      <Link to={boat ? `/boats/${boat.id}` : "/boats"} className="back-link"><ArrowLeft size={16} /> Back to boat</Link>
      <div className="mx-auto mt-6 grid max-w-5xl gap-8 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="panel-card p-6 sm:p-8">
          <span className="eyebrow"><Waves size={15} /> JUST A FEW DETAILS</span><h1 className="heading-lg mt-2">Your time on the water.</h1><p className="mt-2 text-sm text-muted">Review your trip and confirm your reservation.</p>
          <ErrorMessage>{error}</ErrorMessage><SuccessMessage>{message}</SuccessMessage>
          {boat && <div className="mt-7 flex gap-4 border-y border-slate-100 py-5"><img className="h-24 w-32 rounded-xl object-cover" src={boat.image_url} alt={boat.name} /><div><p className="font-display text-lg font-bold text-ink">{boat.name}</p><p className="mt-1 text-sm text-muted">{boat.location}</p><p className="mt-2 text-sm text-muted">{bookingInput.start_date} — {bookingInput.end_date} · {bookingInput.guests} guests</p></div></div>}
          {!booking && <button className="button-primary mt-6 w-full justify-center" disabled={busy || !boat} onClick={confirmBooking}>{busy ? "Checking availability…" : "Confirm booking"} <Check size={17} /></button>}
          {booking && payment && stripePromise && <Elements stripe={stripePromise} options={{ clientSecret: payment.client_secret, appearance: { theme: "stripe", variables: { colorPrimary: "#116e74", borderRadius: "10px" } } }}><CardPayment bookingId={booking.id} onPaid={() => setMessage("Payment submitted. Your booking status will update when Stripe confirms it.")} onError={setError} /></Elements>}
          {booking && !payment && <Link to="/my-bookings" className="button-primary mt-6 w-full justify-center">View my booking <Check size={17} /></Link>}
          {booking && payment && <p className="mt-5 text-center text-xs text-muted"><LockKeyhole size={13} className="mr-1 inline" /> Secured by Stripe test mode</p>}
        </div>
        <aside className="booking-card h-fit">
          <h2 className="font-display text-xl font-bold text-ink">Trip summary</h2>
          {boat && <div className="mt-5 space-y-4 border-b border-slate-100 pb-5 text-sm"><div className="flex justify-between"><span className="text-muted">${Number(boat.price_per_day).toLocaleString()} × {nights} {nights === 1 ? "day" : "days"}</span><span>${(Number(boat.price_per_day) * nights).toLocaleString()}</span></div><div className="flex justify-between"><span className="text-muted">Service fee</span><span>$0</span></div></div>}
          <div className="mt-5 flex justify-between font-display text-lg font-bold text-ink"><span>Total</span><span>${boat ? (Number(boat.price_per_day) * nights).toLocaleString() : "—"}</span></div>
          <p className="mt-5 text-xs leading-5 text-muted">Your dates are checked again when you confirm. Reservations are charged only through the configured Stripe test-mode checkout.</p>
        </aside>
      </div>
    </section>
  );
}
