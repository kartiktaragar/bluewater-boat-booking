import { ArrowRight, Compass, ShieldCheck, Waves } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api";
import BoatCard from "../components/BoatCard";
import { ErrorMessage } from "../components/Feedback";

export default function Home() {
  const [boats, setBoats] = useState([]);
  const [error, setError] = useState("");
  const [searchError, setSearchError] = useState("");
  const [location, setLocation] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    api("/boats").then((items) => setBoats(items.slice(0, 3))).catch((err) => setError(err.message));
  }, []);

  function search(event) {
    event.preventDefault();
    setSearchError("");
    if (Boolean(startDate) !== Boolean(endDate)) {
      setSearchError("Choose both check-in and check-out dates to search availability.");
      return;
    }
    if (startDate && endDate && endDate <= startDate) {
      setSearchError("Check-out must be after check-in.");
      return;
    }
    const params = new URLSearchParams();
    if (location.trim()) params.set("location", location.trim());
    if (startDate) params.set("start_date", startDate);
    if (endDate) params.set("end_date", endDate);
    navigate(`/boats?${params.toString()}`);
  }

  return (
    <>
      <section className="hero">
        <div className="hero-image" />
        <div className="section-wrap hero-inner">
          <div className="max-w-2xl">
            <span className="eyebrow eyebrow-light"><Waves size={15} /> YOUR NEXT GREAT ESCAPE</span>
            <h1 className="hero-title">Find your kind<br />of <span>open water.</span></h1>
            <p className="hero-copy">A slower morning. A wider horizon. Discover boats that make getting away feel effortless.</p>
            <form className="search-panel" onSubmit={search}>
              <label className="search-field"><span>WHERE</span><input value={location} onChange={(e) => setLocation(e.target.value)} placeholder="Coast, city or harbor" /></label>
              <label className="search-field"><span>CHECK IN</span><input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} /></label>
              <label className="search-field"><span>CHECK OUT</span><input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} /></label>
              <button className="button-primary search-button" type="submit"><Compass size={18} /><span>Find a boat</span></button>
            </form>
            {searchError && <p role="alert" className="mt-3 rounded-lg bg-white/95 px-3 py-2 text-xs font-semibold text-red-700">{searchError}</p>}
          </div>
          <p className="hero-caption">The world looks better from here <span>— 32°42' N, 117°09' W</span></p>
        </div>
      </section>
      <section className="section-wrap py-20 sm:py-24">
        <div className="section-heading">
          <div><span className="eyebrow">A LITTLE SALT, A LOT OF SOUL</span><h2 className="heading-lg">The water is calling.</h2></div>
          <Link to="/boats" className="text-link">Explore all boats <ArrowRight size={17} /></Link>
        </div>
        <ErrorMessage>{error}</ErrorMessage>
        {boats.length ? <div className="mt-9 grid gap-6 md:grid-cols-2 lg:grid-cols-3">{boats.map((boat) => <BoatCard key={boat.id} boat={boat} />)}</div> : !error && <div className="py-14 text-center text-muted">Finding your next escape…</div>}
      </section>
      <section className="bg-aqua/60 py-16">
        <div className="section-wrap grid gap-8 md:grid-cols-3">
          {[["01", "A boat for every blue", "From sunset sails to full-week adventures, find the one that feels like yours."], ["02", "The details, sorted", "Clear pricing and thoughtful listings make planning the easy part."], ["03", "Your kind of freedom", "Choose your dates, gather your people, and let the shoreline fall away."]].map(([number, title, text]) => (
            <article key={number} className="feature-card"><span className="feature-number">{number}</span><h3>{title}</h3><p>{text}</p></article>
          ))}
        </div>
      </section>
      <section className="section-wrap flex flex-col items-center justify-between gap-6 py-20 text-center sm:flex-row sm:text-left">
        <div><span className="eyebrow"><ShieldCheck size={15} /> YOUR WATER, YOUR WAY</span><h2 className="heading-lg mt-3">There’s a whole blue out there.</h2></div>
        <Link to="/boats" className="button-primary">Start exploring <ArrowRight size={17} /></Link>
      </section>
    </>
  );
}
