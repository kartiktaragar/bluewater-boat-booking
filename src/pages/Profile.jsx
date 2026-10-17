import { Anchor, Mail, ShieldCheck, UserRound } from "lucide-react";
import { useAuth } from "../auth";

export default function Profile() {
  const { user } = useAuth();
  return (
    <section className="section-wrap min-h-[70vh] py-12 sm:py-16">
      <span className="eyebrow"><UserRound size={15} /> YOUR ACCOUNT</span><h1 className="heading-xl mt-3">A little about you.</h1>
      <div className="profile-card mt-8 max-w-2xl">
        <div className="profile-avatar">{user.full_name.slice(0, 1).toUpperCase()}</div>
        <div className="mt-5"><p className="text-xs font-bold uppercase tracking-wider text-muted">Name</p><p className="mt-1 text-lg font-semibold text-ink">{user.full_name}</p></div>
        <div className="mt-5 flex items-center gap-2"><Mail size={17} className="text-ocean" /><span className="text-sm text-ink">{user.email}</span></div>
        <div className="mt-5 flex items-center gap-2"><ShieldCheck size={17} className="text-ocean" /><span className="text-sm capitalize text-ink">{user.role} account</span></div>
        <div className="mt-7 rounded-xl bg-aqua/60 p-4 text-sm leading-6 text-ink"><Anchor size={16} className="mr-1 inline" /> You’re all set. Your next good day on the water is just a booking away.</div>
      </div>
    </section>
  );
}
