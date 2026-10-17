import { ArrowUpRight, Users } from "lucide-react";
import { Link } from "react-router-dom";

export default function BoatCard({ boat }) {
  return (
    <Link to={`/boats/${boat.id}`} className="boat-card group">
      <div className="boat-card-image-wrap">
        <img src={boat.image_url} alt={boat.name} className="boat-card-image" loading="lazy" />
        <span className="boat-type-pill">{boat.boat_type}</span>
        <span className="boat-card-arrow"><ArrowUpRight size={18} /></span>
      </div>
      <div className="space-y-3 p-5">
        <div className="flex items-start justify-between gap-3">
          <div><p className="text-xs font-semibold uppercase tracking-wider text-muted">{boat.location}</p><h3 className="mt-1 font-display text-xl font-bold text-ink">{boat.name}</h3></div>
          <p className="whitespace-nowrap text-right text-sm font-semibold text-ink">${Number(boat.price_per_day).toLocaleString()}<span className="font-normal text-muted"> / day</span></p>
        </div>
        <div className="flex items-center gap-2 text-sm text-muted"><Users size={16} /> Up to {boat.capacity} guests</div>
      </div>
    </Link>
  );
}
