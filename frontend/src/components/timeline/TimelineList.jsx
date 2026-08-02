import { useState } from "react";
import { severityToColor } from "../cards/ui";

export default function TimelineList({ events }) {
  const [open, setOpen] = useState(null);

  if (!events.length) {
    return <div className="text-tx2 text-[13px] py-6 text-center">Run the investigation to reconstruct the timeline.</div>;
  }

  return (
    <div className="ml-5 pl-7 border-l-2 border-border">
      {events.map((e, i) => (
        <div key={i} className="relative pb-5 cursor-pointer" onClick={() => setOpen(open === i ? null : i)}>
          <span
            className="absolute -left-[34px] top-0.5 w-3.5 h-3.5 rounded-full border-[3px]"
            style={{ background: severityToColor(e.severity), borderColor: "#111827" }}
          />
          <div className="font-mono text-[11px] text-accent font-semibold">{e.time}</div>
          <div className="font-semibold text-[14px] mt-0.5">{e.event}</div>
          {open === i && (
            <div className="mt-2 text-[12px] text-tx2 bg-card2 border border-border rounded-lg px-3 py-2.5">
              <span className="font-mono text-[11px] text-accent">Source: {e.source}</span>
              <br />
              {e.details}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
