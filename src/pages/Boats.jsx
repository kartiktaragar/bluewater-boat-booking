
import { Search, SlidersHorizontal } from "lucide-react";
import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../api";
import BoatCard from "../components/BoatCard";
import { ErrorMessage, LoadingState } from "../components/Feedback";

export default function Boats() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [boats, setBoats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [filters, setFilters] = useState({
    q: searchParams.get("q") || "",
    location: searchParams.get("location") || "",
    guests: searchParams.get("guests") || "",
    start_date: searchParams.get("start_date") || "",
    end_date: searchParams.get("end_date") || "",
  });

  async function loadBoats(values = filters) {
    setLoading(true);
    setError("");

    if (Boolean(values.start_date) !== Boolean(values.end_date)) {
      setError("Choose both dates to filter boats by availability.");
      setLoading(false);
      return;
    }

    if (
      values.start_date &&
      values.end_date &&
      values.end_date <= values.start_date
    ) {
      setError("Check-out must be after check-in.");
      setLoading(false);
      return;
    }

    const params = new URLSearchParams();

    Object.entries(values).forEach(([key, value]) => {
      if (value) params.set(key, value);
    });

    setSearchParams(params, { replace: true });

    try {
      const result = await api(`/boats?${params.toString()}`);

      if (!Array.isArray(result)) {
        throw new Error("Unexpected response from the boats API.");
      }

      setBoats(result);
    } catch (err) {
      setBoats([]);
      setError(err.message || "Unable to load boats. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    const values = {
      q: searchParams.get("q") || "",
      location: searchParams.get("location") || "",
      guests: searchParams.get("guests") || "",
      start_date: searchParams.get("start_date") || "",
      end_date: searchParams.get("end_date") || "",
    };

    setFilters(values);
    loadBoats(values);

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleSubmit(event) {
    event.preventDefault();
    loadBoats();
  }

  return (
    <section className="section-wrap min-h-[70vh] py-12 sm:py-16">
      <div className="max-w-3xl">
        <span className="eyebrow">
          <SlidersHorizontal size={15} /> THE BOAT COLLECTION
        </span>
        <h1 className="heading-xl mt-3">Make a day of it.</h1>
        <p className="mt-3 text-muted">
          Good boats, good people, and nowhere else you need to be.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="filter-panel mt-8">
        <label className="filter-input">
          <span>Search</span>
          <input
            value={filters.q}
            onChange={(e) =>
              setFilters({ ...filters, q: e.target.value })
            }
            placeholder="Boat name, place or vibe"
          />
        </label>

        <label className="filter-input">
          <span>Location</span>
          <input
            value={filters.location}
            onChange={(e) =>
              setFilters({ ...filters, location: e.target.value })
            }
            placeholder="Where to?"
          />
        </label>

        <label className="filter-input">
          <span>Guests</span>
          <input
            type="number"
            min="1"
            value={filters.guests}
            onChange={(e) =>
              setFilters({ ...filters, guests: e.target.value })
            }
            placeholder="Any"
          />
        </label>

        <label className="filter-input">
          <span>From</span>
          <input
            type="date"
            value={filters.start_date}
            onChange={(e) =>
              setFilters({ ...filters, start_date: e.target.value })
            }
          />
        </label>

        <label className="filter-input">
          <span>To</span>
          <input
            type="date"
            value={filters.end_date}
            onChange={(e) =>
              setFilters({ ...filters, end_date: e.target.value })
            }
          />
        </label>

        <button className="button-primary" type="submit">
          <Search size={17} /> Search
        </button>
      </form>

      <ErrorMessage>{error}</ErrorMessage>

      {loading ? (
        <LoadingState label="Finding boats for you…" />
      ) : boats.length > 0 ? (
        <>
          <div className="mt-8 mb-4 text-sm text-muted">
            {boats.length} {boats.length === 1 ? "boat" : "boats"} to explore
          </div>

          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {boats.map((boat) => (
              <BoatCard key={boat.id} boat={boat} />
            ))}
          </div>
        </>
      ) : (
        !error && (
          <div className="empty-state mt-10">
            <div className="empty-icon">
              <Search size={22} />
            </div>
            <h2>No boats found this time.</h2>
            <p>Try another coast, date, or guest count.</p>
          </div>
        )
      )}
    </section>
  );
}
